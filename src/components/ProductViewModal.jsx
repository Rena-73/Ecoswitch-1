import { useState } from 'react'
import { X, Heart, Share2, Star, Loader2 } from 'lucide-react'
import EcoScoreLabel from './EcoScoreLabel'
import { formatRupees } from '../utils/currency'

const ProductViewModal = ({ isOpen, onClose, product, onAddToCart, user, isAddingToCart = false }) => {
  const [selectedImage, setSelectedImage] = useState(0)
  const [quantity, setQuantity] = useState(1)

  if (!isOpen || !product) return null

  // Get product images with fallback
  const getProductImages = () => {
    if (product.images && product.images.length > 0) {
      return product.images.map(img => img.image_url || img.image).filter(Boolean)
    }
    if (product.primary_image) return [product.primary_image]
    if (product.image) return [product.image]
    return [getPlaceholderImage(product.category_name || product.category)]
  }

  const getPlaceholderImage = (category) => {
    const placeholderImages = {
      'Fashion & Accessories': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&h=600&fit=crop',
      'Kitchen & Dining': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop',
      'Home & Garden': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop',
      'Personal Care': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop',
      'Electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&h=600&fit=crop',
      'default': 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop'
    }
    return placeholderImages[category] || placeholderImages.default
  }

  const images = getProductImages()
  const productName = product.name
  const productBrand = product.brand_name || product.brand
  const productPrice = product.price
  const productRating = product.average_rating || product.eco_rating || product.rating
  const productCategory = product.category_name || product.category
  const productDescription = product.description || product.short_description
  const productTags = product.tags || []
  const isInStock = product.is_in_stock !== undefined ? product.is_in_stock : true
  
  // EcoScore data
  const ecoscoreValue = product.ecoscore_value || product.ecoscore?.score_value
  const ecoscoreGrade = product.ecoscore_grade || product.ecoscore?.score_grade

  const handleAddToCart = () => {
    if (onAddToCart) {
      onAddToCart(product, quantity)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">Product Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Product Images */}
            <div className="space-y-4">
              {/* Main Image */}
              <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden">
                <img
                  src={images[selectedImage]}
                  alt={productName}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.src = getPlaceholderImage(productCategory)
                  }}
                />
              </div>

              {/* Thumbnail Images */}
              {images.length > 1 && (
                <div className="flex gap-2 overflow-x-auto">
                  {images.map((image, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImage(index)}
                      className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 ${
                        selectedImage === index ? 'border-green-500' : 'border-gray-200'
                      }`}
                    >
                      <img
                        src={image}
                        alt={`${productName} ${index + 1}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.src = getPlaceholderImage(productCategory)
                        }}
                      />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="space-y-6">
              {/* Basic Info */}
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{productName}</h1>
                <p className="text-xl text-gray-600 mb-4">{productBrand}</p>
                <div className="flex items-center gap-4">
                  <span className="text-3xl font-bold text-green-600">{formatRupees(productPrice)}</span>
                  <div className="flex items-center gap-1">
                    <Star className="w-5 h-5 text-yellow-400 fill-current" />
                    <span className="text-lg font-medium text-gray-700">{productRating}/5</span>
                  </div>
                </div>
              </div>

              {/* EcoScore */}
              {ecoscoreGrade && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-semibold text-green-700">EcoScore:</span>
                  <EcoScoreLabel 
                    score={ecoscoreValue} 
                    grade={ecoscoreGrade} 
                    size="large"
                    showDetails={true}
                  />
                </div>
              )}

              {/* Description */}
              {productDescription && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
                  <p className="text-gray-600 leading-relaxed">{productDescription}</p>
                </div>
              )}

              {/* Tags */}
              {productTags.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Features</h3>
                  <div className="flex flex-wrap gap-2">
                    {productTags.map((tag, i) => (
                      <span 
                        key={i}
                        className="bg-green-50 border border-green-200 text-green-700 text-sm px-3 py-1 rounded-full font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Quantity and Actions */}
              {user && user.user_type === 'customer' && isInStock && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => setQuantity(Math.max(1, quantity - 1))}
                        className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
                      >
                        -
                      </button>
                      <span className="w-12 text-center font-medium text-lg">{quantity}</span>
                      <button
                        onClick={() => setQuantity(quantity + 1)}
                        className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
                      >
                        +
                      </button>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={handleAddToCart}
                      disabled={isAddingToCart}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isAddingToCart ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          <span>Adding to Cart...</span>
                        </>
                      ) : (
                        <>
                          <span>🛒</span>
                          <span>Add to Cart - {formatRupees(productPrice * quantity)}</span>
                        </>
                      )}
                    </button>
                    
                    <button className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                      <Heart className="w-5 h-5 text-gray-600" />
                    </button>
                    
                    <button className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                      <Share2 className="w-5 h-5 text-gray-600" />
                    </button>
                  </div>
                </div>
              )}

              {/* Stock Status */}
              <div className="pt-4 border-t border-gray-200">
                {isInStock ? (
                  <div className="flex items-center gap-2 text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="font-medium">In Stock</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-red-600">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    <span className="font-medium">Out of Stock</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProductViewModal