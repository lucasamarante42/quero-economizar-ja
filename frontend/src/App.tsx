import React, { useState } from 'react';
import axios from 'axios';
import { Search, ShoppingCart, DollarSign, Upload, Trash2 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [shoppingList, setShoppingList] = useState([]);
  const [currentItem, setCurrentItem] = useState({ name: '', quantity: 1, brand: '' });
  const [comparisonResults, setComparisonResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const addItem = () => {
    if (currentItem.name.trim()) {
      setShoppingList([...shoppingList, { ...currentItem }]);
      setCurrentItem({ name: '', quantity: 1, brand: '' });
    }
  };

  const removeItem = (index) => {
    const newList = shoppingList.filter((_, i) => i !== index);
    setShoppingList(newList);
  };

  const comparePrices = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/compare-prices`, shoppingList);
      setComparisonResults(response.data);
    } catch (error) {
      console.error('Error comparing prices:', error);
      alert('Erro ao comparar preços. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('supermarket', 'supermercado_exemplo');

    try {
      await axios.post(`${API_BASE_URL}/api/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert('PDF processado com sucesso!');
    } catch (error) {
      console.error('Error uploading PDF:', error);
      alert('Erro ao processar PDF.');
    } finally {
      setUploading(false);
    }
  };

  const getTotalSavings = () => {
    return comparisonResults.reduce((total, result) => {
      if (result.best_option) {
        const otherPrices = result.results
          .filter(r => r.found && r.supermarket !== result.best_option.supermarket)
          .map(r => r.price);
        
        if (otherPrices.length > 0) {
          const avgPrice = otherPrices.reduce((sum, price) => sum + price, 0) / otherPrices.length;
          return total + (avgPrice - result.best_option.price) * result.item.quantity;
        }
      }
      return total;
    }, 0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-green-600 mb-4">
            Quero Economizar Já
          </h1>
          <p className="text-xl text-gray-600">
            Compare preços de supermercados e economize na sua lista de compras
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Shopping List */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-gray-800 flex items-center">
                <ShoppingCart className="mr-3 text-green-500" />
                Minha Lista de Compras
              </h2>
              <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                {shoppingList.length} itens
              </span>
            </div>

            {/* Add Item Form */}
            <div className="space-y-4 mb-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  type="text"
                  placeholder="Nome do produto"
                  value={currentItem.name}
                  onChange={(e) => setCurrentItem({ ...currentItem, name: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  onKeyPress={(e) => e.key === 'Enter' && addItem()}
                />
                <input
                  type="number"
                  placeholder="Quantidade"
                  value={currentItem.quantity}
                  onChange={(e) => setCurrentItem({ ...currentItem, quantity: parseInt(e.target.value) || 1 })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  min="1"
                />
                <input
                  type="text"
                  placeholder="Marca (opcional)"
                  value={currentItem.brand}
                  onChange={(e) => setCurrentItem({ ...currentItem, brand: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
              <button
                onClick={addItem}
                className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center"
              >
                <Search className="mr-2 h-5 w-5" />
                Adicionar à Lista
              </button>
            </div>

            {/* Shopping List */}
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {shoppingList.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800">{item.name}</h3>
                    <div className="text-sm text-gray-600">
                      Quantidade: {item.quantity} {item.brand && `• Marca: ${item.brand}`}
                    </div>
                  </div>
                  <button
                    onClick={() => removeItem(index)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-full transition duration-200"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="mt-6 space-y-3">
              <button
                onClick={comparePrices}
                disabled={shoppingList.length === 0 || loading}
                className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <>
                    <DollarSign className="mr-2 h-5 w-5" />
                    Comparar Preços
                  </>
                )}
              </button>

              <div className="relative">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  id="pdf-upload"
                />
                <label
                  htmlFor="pdf-upload"
                  className="w-full bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center cursor-pointer"
                >
                  <Upload className="mr-2 h-5 w-5" />
                  {uploading ? 'Processando...' : 'Upload de PDF de Promoção'}
                </label>
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
              <DollarSign className="mr-3 text-blue-500" />
              Resultados da Comparação
            </h2>

            {comparisonResults.length > 0 && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-center">
                  <p className="text-lg font-semibold text-green-800">
                    Economia Total Estimada
                  </p>
                  <p className="text-3xl font-bold text-green-600">
                    R$ {getTotalSavings().toFixed(2)}
                  </p>
                </div>
              </div>
            )}

            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {comparisonResults.map((result, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-lg text-gray-800 mb-3">
                    {result.item.name} × {result.item.quantity}
                  </h3>
                  
                  {result.best_option ? (
                    <div className="space-y-3">
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-semibold text-green-800">
                              Melhor Opção
                            </span>
                            <p className="text-sm text-green-600">
                              {result.best_option.supermarket}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-xl font-bold text-green-800">
                              R$ {result.best_option.price.toFixed(2)}
                            </p>
                            <p className="text-sm text-green-600">
                              Total: R$ {(result.best_option.price * result.item.quantity).toFixed(2)}
                            </p>
                          </div>
                        </div>
                        {result.best_option.promotion && (
                          <span className="inline-block mt-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                            PROMOÇÃO
                          </span>
                        )}
                      </div>

                      {result.results.filter(r => r.found && r.supermarket !== result.best_option.supermarket).length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-600 mb-2">Outras opções:</p>
                          {result.results
                            .filter(r => r.found && r.supermarket !== result.best_option.supermarket)
                            .map((option, optionIndex) => (
                              <div key={optionIndex} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                                <span className="text-sm text-gray-700">{option.supermarket}</span>
                                <span className="text-sm font-medium text-gray-900">
                                  R$ {option.price.toFixed(2)}
                                </span>
                              </div>
                            ))
                          }
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">
                      Nenhum preço encontrado para este produto
                    </p>
                  )}
                </div>
              ))}

              {comparisonResults.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <DollarSign className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>Adicione itens à sua lista e clique em "Comparar Preços" para ver os resultados</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;