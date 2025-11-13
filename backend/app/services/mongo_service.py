from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional
import os
from bson import ObjectId

class MongoService:
	def __init__(self):
		self.client = None
		self.db = None
		self.connect()

	def connect(self):
		"""Conecta ao MongoDB"""
		try:
			mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
			self.client = AsyncIOMotorClient(mongo_url)
			self.db = self.client["economizar_ja"]
			self.products = self.db["products"]
			print("Conectado ao MongoDB com sucesso!")
		except Exception as e:
			print(f"Erro ao conectar ao MongoDB: {e}")

	async def store_products(self, products: List[Dict], supermarket: str):
		"""Armazena produtos no banco de dados"""
		if not products:
			print("Nenhum produto para armazenar")
			return

		try:
			# Remove produtos antigos deste supermercado
			delete_result = await self.products.delete_many({"supermarket": supermarket})
			print(f"Removidos {delete_result.deleted_count} produtos antigos de {supermarket}")

			# Insere novos produtos
			insert_result = await self.products.insert_many(products)
			print(f"Inseridos {len(insert_result.inserted_ids)} produtos de {supermarket}")

		except Exception as e:
			print(f"Erro ao armazenar produtos: {e}")

	async def search_products(self, product_name: str, brand: Optional[str] = None) -> List[Dict]:
		"""Busca produtos por nome e marca opcional"""
		try:
			# Cria query de busca
			query = {
				"name": {"$regex": product_name, "$options": "i"}
			}

			if brand:
				query["brand"] = {"$regex": brand, "$options": "i"}

			cursor = self.products.find(query)
			products = await cursor.to_list(length=100)

			# Converte ObjectId para string para serialização
			for product in products:
				product["_id"] = str(product["_id"])

			return products

		except Exception as e:
			print(f"Erro ao buscar produtos: {e}")
			return []

	async def get_available_supermarkets(self) -> List[str]:
		"""Obtém lista de supermercados disponíveis"""
		try:
			supermarkets = await self.products.distinct("supermarket")
			return supermarkets
		except Exception as e:
			print(f"Erro ao obter supermercados: {e}")
			return []

	async def get_products_by_supermarket(self, supermarket: str) -> List[Dict]:
		"""Obtém todos os produtos de um supermercado"""
		try:
			cursor = self.products.find({"supermarket": supermarket})
			products = await cursor.to_list(length=1000)

			for product in products:
				product["_id"] = str(product["_id"])

			return products
		except Exception as e:
			print(f"Erro ao obter produtos do supermercado: {e}")
			return []