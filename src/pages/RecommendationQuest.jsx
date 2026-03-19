import { useState, useEffect } from 'react';
import { ChevronRight, Zap, Leaf, Heart, Target } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import { getSmartRecommendations, getRecommendationMessage } from '../utils/nlpRecommendation';
import ecoscoreProducts from '../data/ecoscoreProducts';

const API_BASE = import.meta.env?.VITE_API_BASE || window.__API_BASE__ || 'http://127.0.0.1:8001';

const RecommendationQuest = ({ setCurrentPage }) => {
  const [currentStep, setCurrentStep] = useState('welcome');
  const [recommendations, setRecommendations] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [userAnswers, setUserAnswers] = useState({
    name: '',
    concern: '',
    lifestyle: '',
    interest: '',
    customNeed: ''
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setIsLoading(true);
      
      // Try to fetch from API first
      const ecoscoreResponse = await fetch(`${API_BASE}/api/ecoscore/products-ecoscore/`);
      if (ecoscoreResponse.ok) {
        const data = await ecoscoreResponse.json();
        const results = data.results || data;
        if (Array.isArray(results) && results.length > 0) {
          setAllProducts(results);
          return;
        }
      }

      // Fallback to mock data
      setAllProducts(ecoscoreProducts);
    } catch (error) {
      console.error('Error fetching products:', error);
      setAllProducts(ecoscoreProducts);
    } finally {
      setIsLoading(false);
    }
  };

  const generateRecommendations = (answers) => {
    // Build a comprehensive query from answers
    const queryParts = [];
    
    if (answers.concern) queryParts.push(answers.concern);
    if (answers.lifestyle) queryParts.push(answers.lifestyle);
    if (answers.interest) queryParts.push(answers.interest);
    if (answers.customNeed) queryParts.push(answers.customNeed);

    const comprehensiveQuery = queryParts.join(' ').trim();
    const recs = getSmartRecommendations(comprehensiveQuery, allProducts);
    
    setRecommendations(recs);
    setCurrentStep('results');
  };

  const handleQuestionAnswer = (field, value) => {
    setUserAnswers(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNextStep = () => {
    switch (currentStep) {
      case 'welcome':
        setCurrentStep('concern');
        break;
      case 'concern':
        setCurrentStep('lifestyle');
        break;
      case 'lifestyle':
        setCurrentStep('interest');
        break;
      case 'interest':
        setCurrentStep('custom');
        break;
      case 'custom':
        generateRecommendations(userAnswers);
        break;
      default:
        break;
    }
  };

  const handlePrevStep = () => {
    switch (currentStep) {
      case 'concern':
        setCurrentStep('welcome');
        break;
      case 'lifestyle':
        setCurrentStep('concern');
        break;
      case 'interest':
        setCurrentStep('lifestyle');
        break;
      case 'custom':
        setCurrentStep('interest');
        break;
      case 'results':
        setCurrentStep('custom');
        break;
      default:
        break;
    }
  };

  const resetQuest = () => {
    setUserAnswers({
      name: '',
      concern: '',
      lifestyle: '',
      interest: '',
      customNeed: ''
    });
    setCurrentStep('welcome');
    setRecommendations([]);
  };

  const isReadyForNext = () => {
    switch (currentStep) {
      case 'welcome':
        return true;
      case 'concern':
        return userAnswers.concern !== '';
      case 'lifestyle':
        return userAnswers.lifestyle !== '';
      case 'interest':
        return userAnswers.interest !== '';
      case 'custom':
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-green-100 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-block bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-full px-6 py-2 mb-4">
            🌿 Personalized Recommendation Quest
          </div>
          <h1 className="text-4xl font-bold text-green-800 mb-4">
            Find Your Perfect Eco Products
          </h1>
          <p className="text-gray-600 text-lg">
            Just a few questions to discover sustainable products tailored to your lifestyle
          </p>
        </div>

        {/* Progress Bar */}
        {currentStep !== 'welcome' && currentStep !== 'results' && (
          <div className="mb-8">
            <div className="flex justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700">Progress</span>
              <span className="text-sm font-semibold text-gray-700">
                {currentStep === 'concern' ? '1/4' : 
                 currentStep === 'lifestyle' ? '2/4' : 
                 currentStep === 'interest' ? '3/4' : '4/4'}
              </span>
            </div>
            <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-green-600 to-blue-600 transition-all duration-300"
                style={{
                  width: currentStep === 'concern' ? '25%' : 
                         currentStep === 'lifestyle' ? '50%' : 
                         currentStep === 'interest' ? '75%' : '100%'
                }}
              />
            </div>
          </div>
        )}

        {/* Welcome Screen */}
        {currentStep === 'welcome' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <Leaf className="w-12 h-12 text-green-600 mx-auto mb-3" />
                <h3 className="font-semibold text-green-800 mb-2">Personalized</h3>
                <p className="text-sm text-gray-600">Recommendations tailored to you</p>
              </div>
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <Zap className="w-12 h-12 text-blue-600 mx-auto mb-3" />
                <h3 className="font-semibold text-blue-800 mb-2">Quick Quiz</h3>
                <p className="text-sm text-gray-600">Takes just 2 minutes</p>
              </div>
              <div className="text-center p-6 bg-purple-50 rounded-lg">
                <Heart className="w-12 h-12 text-purple-600 mx-auto mb-3" />
                <h3 className="font-semibold text-purple-800 mb-2">Smart Matching</h3>
                <p className="text-sm text-gray-600">AI-powered matching</p>
              </div>
            </div>

            <div className="text-center mb-8">
              <p className="text-gray-700 mb-6 text-lg">
                Ready to discover eco-friendly products that match your lifestyle? Let's get started! 🚀
              </p>
            </div>

            <button
              onClick={handleNextStep}
              className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 text-lg"
            >
              Start Recommendation Quest <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Concern Question */}
        {currentStep === 'concern' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
            <h2 className="text-2xl font-bold text-green-800 mb-6">
              What's your main eco concern? 🌍
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {[
                { value: 'plastic-free sustainable products', label: '♻️ Plastic-Free Living', emoji: '🚫' },
                { value: 'organic natural skincare', label: '🌱 Organic & Natural', emoji: '🌿' },
                { value: 'vegan cruelty-free beauty', label: '🐰 Cruelty-Free', emoji: '❤️' },
                { value: 'sustainable clothing fashion', label: '👕 Sustainable Fashion', emoji: '👗' },
                { value: 'eco-friendly home products', label: '🏠 Green Home', emoji: '🏡' },
                { value: 'zero waste lifestyle', label: '♻️ Zero Waste', emoji: '🌎' }
              ].map(option => (
                <button
                  key={option.value}
                  onClick={() => handleQuestionAnswer('concern', option.value)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    userAnswers.concern === option.value
                      ? 'border-green-600 bg-green-50'
                      : 'border-gray-300 hover:border-green-400'
                  }`}
                >
                  <div className="text-2xl mb-2">{option.emoji}</div>
                  <div className="font-semibold text-gray-800">{option.label}</div>
                </button>
              ))}
            </div>

            <div className="flex gap-4">
              <button
                onClick={handlePrevStep}
                className="flex-1 border-2 border-gray-300 font-semibold py-3 px-6 rounded-lg transition-all hover:bg-gray-50"
              >
                Back
              </button>
              <button
                onClick={handleNextStep}
                disabled={!isReadyForNext()}
                className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-all"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Lifestyle Question */}
        {currentStep === 'lifestyle' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
            <h2 className="text-2xl font-bold text-green-800 mb-6">
              What's your lifestyle? 🎯
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {[
                { value: 'busy professional quick convenient', label: '⚡ Busy Professional', emoji: '💼' },
                { value: 'active fitness sports athlete', label: '🏃 Active Lifestyle', emoji: '💪' },
                { value: 'travel portable compact on-the-go', label: '✈️ Frequent Traveler', emoji: '🧳' },
                { value: 'family kids household', label: '👨‍👩‍👧‍👦 Family-Focused', emoji: '👶' },
                { value: 'minimal simplify declutter', label: '📦 Minimalist', emoji: '🌾' },
                { value: 'homebody comfort cozy', label: '🏠 Homebody', emoji: '🛋️' }
              ].map(option => (
                <button
                  key={option.value}
                  onClick={() => handleQuestionAnswer('lifestyle', option.value)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    userAnswers.lifestyle === option.value
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-300 hover:border-blue-400'
                  }`}
                >
                  <div className="text-2xl mb-2">{option.emoji}</div>
                  <div className="font-semibold text-gray-800">{option.label}</div>
                </button>
              ))}
            </div>

            <div className="flex gap-4">
              <button
                onClick={handlePrevStep}
                className="flex-1 border-2 border-gray-300 font-semibold py-3 px-6 rounded-lg transition-all hover:bg-gray-50"
              >
                Back
              </button>
              <button
                onClick={handleNextStep}
                disabled={!isReadyForNext()}
                className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-all"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Interest Question */}
        {currentStep === 'interest' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
            <h2 className="text-2xl font-bold text-green-800 mb-6">
              What product category interests you? 🛍️
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {[
                { value: 'skincare face cream moisturizer', label: '💆 Skincare', emoji: '✨' },
                { value: 'haircare shampoo conditioner', label: '💇 Haircare', emoji: '💁' },
                { value: 'kitchen cooking utensils', label: '🍳 Kitchen', emoji: '🥘' },
                { value: 'clothing apparel fashion wear', label: '👕 Clothing', emoji: '👖' },
                { value: 'home decor furniture', label: '🪑 Home', emoji: '🛁' },
                { value: 'beauty cosmetics makeup', label: '💄 Beauty', emoji: '💅' }
              ].map(option => (
                <button
                  key={option.value}
                  onClick={() => handleQuestionAnswer('interest', option.value)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    userAnswers.interest === option.value
                      ? 'border-purple-600 bg-purple-50'
                      : 'border-gray-300 hover:border-purple-400'
                  }`}
                >
                  <div className="text-2xl mb-2">{option.emoji}</div>
                  <div className="font-semibold text-gray-800">{option.label}</div>
                </button>
              ))}
            </div>

            <div className="flex gap-4">
              <button
                onClick={handlePrevStep}
                className="flex-1 border-2 border-gray-300 font-semibold py-3 px-6 rounded-lg transition-all hover:bg-gray-50"
              >
                Back
              </button>
              <button
                onClick={handleNextStep}
                disabled={!isReadyForNext()}
                className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-all"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Custom Need Question */}
        {currentStep === 'custom' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
            <h2 className="text-2xl font-bold text-green-800 mb-6">
              Any specific needs? (Optional) 💭
            </h2>

            <p className="text-gray-600 mb-4">
              Tell us anything else about what you're looking for - allergies, budget, specific brands, etc.
            </p>

            <textarea
              value={userAnswers.customNeed}
              onChange={(e) => handleQuestionAnswer('customNeed', e.target.value)}
              placeholder="e.g., 'I have sensitive skin and prefer affordable organic products' or 'Looking for budget-friendly options under ₹500'"
              className="w-full border-2 border-gray-300 rounded-lg p-4 mb-8 min-h-32 focus:outline-none focus:border-green-600"
            />

            <div className="flex gap-4">
              <button
                onClick={handlePrevStep}
                className="flex-1 border-2 border-gray-300 font-semibold py-3 px-6 rounded-lg transition-all hover:bg-gray-50"
              >
                Back
              </button>
              <button
                onClick={handleNextStep}
                className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
              >
                Get Recommendations <Zap className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Results Screen */}
        {currentStep === 'results' && (
          <div>
            <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-2xl shadow-xl p-8 md:p-12 mb-8">
              <Target className="w-12 h-12 mb-4" />
              <h2 className="text-3xl font-bold mb-4">
                Perfect Matches Found! ✨
              </h2>
              <p className="text-green-100 text-lg">
                Here are your personalized {getRecommendationMessage({ 
                  categories: userAnswers.concern.split(' '),
                  emotions: [],
                  lifestyle: userAnswers.lifestyle.split(' ')
                })} recommendations
              </p>
            </div>

            {isLoading ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
              </div>
            ) : recommendations.length > 0 ? (
              <>
                <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 mb-8">
                  {recommendations.map((product, index) => (
                    <ProductCard key={product.id || index} product={product} />
                  ))}
                </div>

                <button
                  onClick={() => setCurrentPage('products')}
                  className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-bold py-4 px-6 rounded-lg transition-all mb-4"
                >
                  View All Products
                </button>
              </>
            ) : (
              <div className="bg-white rounded-2xl shadow-lg p-8 text-center mb-8">
                <p className="text-gray-600 mb-4">
                  No exact matches found, but check out our full product range!
                </p>
                <button
                  onClick={() => setCurrentPage('products')}
                  className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg transition-all"
                >
                  Browse All Products
                </button>
              </div>
            )}

            <button
              onClick={resetQuest}
              className="w-full border-2 border-gray-300 font-semibold py-3 px-6 rounded-lg transition-all hover:bg-gray-50"
            >
              Start Over
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationQuest;
