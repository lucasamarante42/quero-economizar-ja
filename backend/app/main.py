from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from prometheus_client import make_asgi_app, Counter, Histogram
import time
import os

from app.models import ShoppingItem, ComparisonResult
from app.services.pdf_processor import PDFProcessor
from app.services.price_comparator import PriceComparator
from app.services.mongo_service import MongoService

from typing import List, Optional, Dict, Any

# Configuração da aplicação
app = FastAPI(
    title="Quero Economizar Já API",
    description="API para comparação de preços de supermercados",
    version="1.0.0"
)

# Métricas Prometheus
REQUEST_COUNT = Counter('requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')

# App Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serviços
pdf_processor = PDFProcessor()
price_comparator = PriceComparator()
mongo_service = MongoService()

# Middleware para métricas
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    
    return response

# Rotas
@app.get("/")
async def root():
    return {
        "message": "Bem-vindo ao Quero Economizar Já API",
        "version": "1.0.0",
        "endpoints": {
            "documentation": "/docs",
            "metrics": "/metrics",
            "upload_pdf": "/api/upload-pdf",
            "compare_prices": "/api/compare-prices",
            "supermarkets": "/api/supermarkets"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(..., description="Arquivo PDF com promoções"),
    supermarket: str = Query("supermercado", description="Nome do supermercado")
):
    """
    Faz upload de PDF de promoções e processa os produtos
    """
    start_time = time.time()
    
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="O arquivo deve ser um PDF"
            )
        
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Arquivo vazio"
            )
        
        print(f"Processando PDF {file.filename} para {supermarket}...")
        
        products = await pdf_processor.process_pdf(content, supermarket)
        await mongo_service.store_products(products, supermarket)
        
        latency = time.time() - start_time
        print(f"PDF processado em {latency:.2f}s - {len(products)} produtos")
        
        return {
            "message": "PDF processado com sucesso",
            "supermarket": supermarket,
            "products_processed": len(products),
            "processing_time": f"{latency:.2f}s"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro no upload do PDF: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao processar PDF: {str(e)}"
        )

@app.post("/api/compare-prices")
async def compare_prices(shopping_list: List[ShoppingItem]):
    """
    Compara preços para uma lista de compras
    """
    start_time = time.time()
    
    try:
        if not shopping_list:
            raise HTTPException(
                status_code=400, 
                detail="Lista de compras vazia"
            )
        
        print(f"Comparando preços para {len(shopping_list)} itens...")
        
        comparison_results = []
        
        for item in shopping_list:
            results = await price_comparator.find_best_prices(item)
            best_option = price_comparator.get_best_option(results)
            
            # Para Pydantic 1.x, use dict() em vez de model_dump()
            comparison_results.append({
                "item": item.dict(),
                "results": results,
                "best_option": best_option
            })
        
        latency = time.time() - start_time
        print(f"Comparação concluída em {latency:.2f}s")
        
        return comparison_results
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro na comparação de preços: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao comparar preços: {str(e)}"
        )

@app.get("/api/supermarkets")
async def get_supermarkets():
    """
    Retorna lista de supermercados disponíveis
    """
    try:
        supermarkets = await mongo_service.get_available_supermarkets()
        return {
            "supermarkets": supermarkets,
            "count": len(supermarkets)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter supermercados: {str(e)}"
        )

@app.get("/api/products/{supermarket}")
async def get_products(supermarket: str):
    """
    Retorna produtos de um supermercado específico
    """
    try:
        products = await mongo_service.get_products_by_supermarket(supermarket)
        return {
            "supermarket": supermarket,
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter produtos: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )