import re
from typing import List

def clean_product_name(name: str) -> str:
	"""
	Limpa e formata o nome do produto removendo caracteres especiais
	e palavras desnecessárias
	"""
	if not name or not isinstance(name, str):
		return ""

	# Remove caracteres especiais, mantendo acentos e espaços
	name = re.sub(r'[^\w\sÀ-ÿ]', ' ', name, flags=re.UNICODE)

	# Remove excesso de espaços
	name = re.sub(r'\s+', ' ', name).strip()

	# Remove palavras comuns que não são parte do nome do produto
	stop_words = {
		'unidade', 'kg', 'gr', 'g', 'ml', 'litro', 'l', 'pack', 'cx', 'pct',
		'und', 'pc', 'dv', 'fw', 'cv', 'pv', 'sc', 'ct', 'cp', 'tb', 'pt'
	}

	words = [
		word for word in name.split()
		if word.lower() not in stop_words and len(word) > 1
	]

	cleaned_name = ' '.join(words).title()

	# Se após limpeza o nome ficou muito curto, retorna o original limpo
	if len(cleaned_name) < 3:
		return ' '.join(re.sub(r'[^\w\sÀ-ÿ]', ' ', name, flags=re.UNICODE).split()).title()

	return cleaned_name

def extract_price(text: str) -> float:
	"""
	Extrai preço do texto usando múltiplos padrões
	"""
	if not text:
		return None

	# Padrões de preço em ordem de prioridade
	price_patterns = [
		r'R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',          # R$ 1.999,99
		r'R\$\s*(\d{1,3}(?:\.\d{3})*\.\d{2})',         # R$ 1.999.99
		r'RS\s*(\d{1,3}(?:\.\d{3})*,\d{2})',           # RS 1.999,99
		r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*R\$',          # 1.999,99 R$
		r'\b(\d{1,3}(?:\.\d{3})*,\d{2})\b',            # 1.999,99
		r'\b(\d{1,3}(?:\.\d{3})*\.\d{2})\b',           # 1.999.99
		r'\b(\d+,\d{2})\b',                            # 99,99
		r'\b(\d+\.\d{2})\b',                           # 99.99
	]

	for pattern in price_patterns:
		matches = re.findall(pattern, text)
		if matches:
			try:
				price_str = matches[0]
				# Remove pontos de milhar e converte decimal
				if '.' in price_str and ',' in price_str:
					# Formato 1.999,99 -> remove ponto, substitui vírgula
					price_str = price_str.replace('.', '').replace(',', '.')
				elif ',' in price_str:
					# Formato 99,99 -> substitui vírgula
					price_str = price_str.replace(',', '.')

				price = float(price_str)

				# Validação: preço deve ser razoável (entre 0.01 e 9999.99)
				if 0.01 <= price <= 9999.99:
					return price

			except (ValueError, IndexError):
				continue

	return None

def is_product_line(line: str) -> bool:
	"""
	Verifica se a linha parece conter um produto
	"""
	if not line or len(line.strip()) < 3:
		return False

	line_lower = line.lower().strip()

	# Ignora linhas que são claramente cabeçalhos/seções
	ignore_patterns = [
		'promoção', 'ofertas', 'validade', 'página', 'pagina', 'caderno',
		'semana', 'supermercado', 'mercado', 'unidade', 'kg', 'gr', 'ml',
		'levou', 'pagou', 'leve%', 'pague%', 'confira', 'destaque'
	]

	if any(pattern in line_lower for pattern in ignore_patterns):
		return False

	# Ignora linhas que são apenas números ou caracteres especiais
	if re.match(r'^[\d\s\.\,]+$', line):
		return False

	# Deve conter pelo menos uma letra
	if not re.search(r'[a-zA-ZÀ-ÿ]', line):
		return False

	return True

def is_promotion_line(line: str) -> bool:
	"""
	Verifica se a linha indica promoção
	"""
	if not line:
		return False

	line_lower = line.lower()

	promo_keywords = [
		'promoção', 'oferta', 'desconto', 'leve', 'pague', 'leve%', 'pague%',
		'imperdível', 'imperdivel', 'black', 'sexta', 'super', 'mega', 'quinta'
	]

	return any(keyword in line_lower for keyword in promo_keywords)

def categorize_product(product_name: str) -> str:
	"""
	Categoriza produtos baseado em palavras-chave
	"""
	if not product_name:
		return "outros"

	name_lower = product_name.lower()

	categories = {
		'hortifruti': [
			'alface', 'tomate', 'cebola', 'batata', 'cenoura', 'fruta', 'verdura',
			'legume', 'banana', 'laranja', 'maçã', 'maca', 'abacaxi', 'limão', 'limao',
			'couve', 'repolho', 'beterraba', 'abobora', 'abóbora', 'melancia', 'uva'
		],
		'carnes': [
			'carne', 'frango', 'peixe', 'bovina', 'suína', 'suina', 'bacon',
			'contra', 'file', 'filé', 'picanha', 'alcatra', 'costela', 'linguiça',
			'linguica', 'salsicha', 'presunto', 'mortadela', 'salame'
		],
		'laticinios': [
			'leite', 'queijo', 'manteiga', 'iogurte', 'requeijão', 'requeijao',
			'creme', 'nata', 'yogurte', 'coalhada', 'parmesão', 'parmesao'
		],
		'bebidas': [
			'refrigerante', 'suco', 'água', 'agua', 'energético', 'energetico', 'isotônico', 'isotonico'
		],
		'limpeza': [
			'sabão', 'sabao', 'detergente', 'álcool', 'alcool', 'desinfetante',
			'limpa', 'multiuso', 'amaciante', 'água sanitária', 'agua sanitaria',
			'lustra', 'pano', 'esponja', 'vassoura', 'rodo'
		],
		'padaria': [
			'pão', 'pao', 'bolo', 'bisnaga', 'francês', 'frances', 'caseiro',
			'croissant', 'baguete', 'broa', 'sonho', 'torta', 'bolacha', 'biscoito'
		],
		'mercearia': [
			'arroz', 'feijão', 'feijao', 'açúcar', 'acucar', 'café', 'cafe',
			'óleo', 'oleo', 'farinha', 'macarrão', 'macarrao', 'molho', 'extrato',
			'sal', 'tempero', 'conserva', 'lata', 'enlatado'
		],
		'higiene': [
			'shampoo', 'condicionador', 'sabonete', 'creme dental', 'pasta dental',
			'escova', 'papel higiênico', 'papel higienico', 'absorvente', 'fralda',
			'desodorante', 'perfume', 'colônia', 'colonia'
		]
	}

	for category, keywords in categories.items():
		if any(keyword in name_lower for keyword in keywords):
			return category

	return 'outros'