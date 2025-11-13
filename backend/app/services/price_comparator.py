from typing import List, Dict, Optional
from app.models import ShoppingItem
from app.services.mongo_service import MongoService

class PriceComparator:
    def __init__(self):
        self.mongo_service = MongoService()
    
    async def find_best_prices(self, item: ShoppingItem) -> List[Dict]:
        """
        Encontra preços para um item específico em todos os supermercados
        """
        try:
            # Busca produtos similares no banco
            products = await self.mongo_service.search_products(item.name, item.brand)
            
            results = []
            for product in products:
                results.append({
                    'supermarket': product['supermarket'],
                    'product_name': product['name'],
                    'price': float(product['price']),
                    'promotion': product.get('promotion', False),
                    'found': True
                })
            
            # Se não encontrou resultados, retorna resultado não encontrado
            if not results:
                return [{
                    'supermarket': 'Nenhum',
                    'product_name': item.name,
                    'price': 0.0,
                    'promotion': False,
                    'found': False
                }]
            
            return results
            
        except Exception as e:
            print(f"Erro ao buscar melhores preços: {e}")
            return []
    
    def get_best_option(self, results: List[Dict]) -> Optional[Dict]:
        """
        Obtém a melhor opção de preço dos resultados
        """
        if not results:
            return None
        
        # Filtra apenas produtos encontrados
        valid_results = [r for r in results if r['found']]
        if not valid_results:
            return None
        
        # Ordena por preço e retorna o mais barato
        best_option = min(valid_results, key=lambda x: x['price'])
        return best_option
    
    async def compare_shopping_list(self, shopping_list: List[ShoppingItem]) -> List[Dict]:
        """
        Compara preços para uma lista de compras completa
        """
        comparison_results = []
        
        for item in shopping_list:
            results = await self.find_best_prices(item)
            best_option = self.get_best_option(results)
            
            # Usar item.dict() para versões mais recentes do Pydantic
            # ou item.model_dump() para versões mais antigas
            try:
                item_dict = item.dict()
            except AttributeError:
                item_dict = item.model_dump()
            
            comparison_results.append({
                'item': item_dict,
                'results': results,
                'best_option': best_option
            })
        
        return comparison_results