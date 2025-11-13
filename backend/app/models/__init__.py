from pydantic import BaseModel
from typing import List, Optional

class ShoppingItem(BaseModel):
	name: str
	quantity: int = 1
	brand: Optional[str] = None

class PriceResult(BaseModel):
	supermarket: str
	product_name: str
	price: float
	promotion: bool
	found: bool

class ComparisonResult(BaseModel):
	item: ShoppingItem
	results: List[PriceResult]
	best_option: Optional[PriceResult]

class Product(BaseModel):
	name: str
	price: float
	supermarket: str
	promotion: bool = False
	category: str = "outros"