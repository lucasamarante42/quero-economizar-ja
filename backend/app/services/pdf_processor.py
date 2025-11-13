import pdfplumber
import pandas as pd
from typing import List, Dict
import aiofiles
import asyncio

from app.utils.helpers import (
	clean_product_name,
	extract_price,
	is_product_line,
	is_promotion_line,
	categorize_product
)

class PDFProcessor:
	def __init__(self):
		self.min_confidence = 0.6

	async def process_pdf(self, pdf_content: bytes, supermarket: str = "supermercado") -> List[Dict]:
		"""
		Processa PDF content e extrai informações dos produtos
		"""
		products = []

		try:
			with pdfplumber.open(pdf_content) as pdf:
				for page_num, page in enumerate(pdf.pages):
					print(f"Processando página {page_num + 1}...")

					# Estratégia 1: Tenta extrair tabelas
					table_products = await self._extract_from_tables(page, supermarket)
					products.extend(table_products)

					# Estratégia 2: Extrai do texto
					text_products = await self._extract_from_text(page, supermarket)
					products.extend(text_products)

					print(f"Página {page_num + 1}: {len(table_products) + len(text_products)} produtos encontrados")

		except Exception as e:
			print(f"Erro ao processar PDF: {e}")
			# Fallback: tenta processar apenas o texto
			try:
				with pdfplumber.open(pdf_content) as pdf:
					for page in pdf.pages:
						text_products = await self._extract_from_text(page, supermarket)
						products.extend(text_products)
			except Exception as fallback_error:
				print(f"Erro no fallback: {fallback_error}")

		# Remove duplicatas e produtos inválidos
		valid_products = self._filter_valid_products(products)
		print(f"Total de produtos válidos encontrados: {len(valid_products)}")

		return valid_products

	async def _extract_from_tables(self, page, supermarket: str) -> List[Dict]:
		"""
		Extrai produtos de tabelas detectadas no PDF
		"""
		products = []

		try:
			tables = page.extract_tables()
			if not tables:
				return products

			for table_num, table in enumerate(tables):
				for row_num, row in enumerate(table):
					if not row or len(row) < 2:
						continue

					# Combina todo o texto da linha para análise
					row_text = ' '.join([str(cell) if cell else '' for cell in row])

					# Tenta encontrar produto e preço na linha
					product_info = await self._extract_product_from_line(row_text, supermarket)
					if product_info:
						products.append(product_info)

					# Se não encontrou, tenta combinar células
					else:
						# Procura preço nas últimas células (comum em tabelas)
						for i in range(len(row) - 1, -1, -1):
							cell_text = str(row[i]) if row[i] else ""
							price = extract_price(cell_text)
							if price:
								# Procura nome do produto nas células anteriores
								product_name = ""
								for j in range(i):
									if row[j] and len(str(row[j])) > 2:
										candidate = clean_product_name(str(row[j]))
										if candidate and len(candidate) > 3:
											product_name = candidate
											break

								if product_name:
									products.append({
										'name': product_name,
										'price': price,
										'supermarket': supermarket,
										'promotion': is_promotion_line(row_text),
										'category': categorize_product(product_name)
									})
								break

		except Exception as e:
			print(f"Erro ao extrair de tabelas: {e}")

		return products

	async def _extract_from_text(self, page, supermarket: str) -> List[Dict]:
		"""
		Extrai produtos do texto da página
		"""
		products = []

		try:
			text = page.extract_text()
			if not text:
				return products

			lines = text.split('\n')
			i = 0

			while i < len(lines):
				line = lines[i].strip()

				if is_product_line(line):
					product_info = await self._extract_product_from_line(line, supermarket)

					if product_info:
						products.append(product_info)
						i += 1
					else:
						# Se não encontrou produto completo, tenta com próxima linha
						if i + 1 < len(lines):
							combined_line = line + " " + lines[i + 1].strip()
							combined_product_info = await self._extract_product_from_line(combined_line, supermarket)

							if combined_product_info:
								products.append(combined_product_info)
								i += 2  # Consome duas linhas
							else:
								i += 1
						else:
							i += 1
				else:
					i += 1

		except Exception as e:
			print(f"Erro ao extrair do texto: {e}")

		return products

	async def _extract_product_from_line(self, line: str, supermarket: str) -> Dict:
		"""
		Extrai informações do produto de uma linha de texto
		"""
		try:
			price = extract_price(line)
			if not price:
				return None

			# Remove o preço da linha para obter o nome do produto
			product_line = line
			for pattern in [
				r'R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}',
				r'R\$\s*\d{1,3}(?:\.\d{3})*\.\d{2}',
				r'RS\s*\d{1,3}(?:\.\d{3})*,\d{2}',
				r'\d{1,3}(?:\.\d{3})*,\d{2}\s*R\$',
				r'\b\d{1,3}(?:\.\d{3})*,\d{2}\b',
				r'\b\d{1,3}(?:\.\d{3})*\.\d{2}\b',
				r'\b\d+,\d{2}\b',
				r'\b\d+\.\d{2}\b'
			]:
				product_line = re.sub(pattern, '', product_line)

			product_name = clean_product_name(product_line.strip())

			if not product_name or len(product_name) < 3:
				return None

			return {
				'name': product_name,
				'price': price,
				'supermarket': supermarket,
				'promotion': is_promotion_line(line),
				'category': categorize_product(product_name)
			}

		except Exception as e:
			print(f"Erro ao extrair produto da linha: {e}")
			return None

	def _filter_valid_products(self, products: List[Dict]) -> List[Dict]:
		"""
		Filtra produtos válidos e remove duplicatas
		"""
		valid_products = []
		seen_products = set()

		for product in products:
			try:
				# Validações básicas
				if not product.get('name') or len(product['name']) < 3:
					continue

				if not isinstance(product.get('price'), (int, float)) or product['price'] <= 0:
					continue

				# Cria uma chave única para evitar duplicatas
				product_key = (
					product['name'].lower().strip(),
					round(product['price'], 2),
					product['supermarket']
				)

				if product_key not in seen_products:
					seen_products.add(product_key)
					valid_products.append(product)

			except Exception as e:
				print(f"Erro ao validar produto: {e}")
				continue

		return valid_products