/**
 * NLP-based Recommendation Engine
 * Uses natural language processing to provide intelligent product recommendations
 */

// Keyword mappings for various product categories and needs
const keywordMappings = {
  skincare: ['face', 'skin', 'cream', 'moisturizer', 'serum', 'lotion', 'cleanser', 'soap', 'wash', 'facial'],
  haircare: ['hair', 'shampoo', 'conditioner', 'oil', 'scalp', 'head', 'curl', 'treatment'],
  organic: ['organic', 'bio', 'natural', 'chemical-free', 'pure', 'ayurvedic', 'herbal'],
  sustainable: ['eco-friendly', 'sustainable', 'green', 'environment', 'planet', 'ecological', 'organic'],
  plastic_free: ['plastic-free', 'no plastic', 'biodegradable', 'compostable', 'zero waste', 'packaging'],
  vegan: ['vegan', 'cruelty-free', 'animal-free', 'no animal'],
  kitchen: ['kitchen', 'cooking', 'utensil', 'cookware', 'dishware', 'pot', 'pan', 'cutlery'],
  clothing: ['cloth', 'wear', 'apparel', 'shirt', 'pants', 'dress', 'fabric', 'textile', 'cotton'],
  home: ['home', 'house', 'room', 'decor', 'bed', 'pillow', 'sheet', 'towel', 'curtain'],
  personal: ['personal', 'hygiene', 'care', 'deodorant', 'body', 'hand'],
  baby: ['baby', 'infant', 'child', 'kid', 'diaper', 'toy', 'nursery'],
  beauty: ['beauty', 'makeup', 'cosmetics', 'lips', 'eyes', 'nails', 'perfume'],
  wellness: ['health', 'wellness', 'vitamin', 'supplement', 'yoga', 'meditation', 'fitness'],
  budget: ['cheap', 'affordable', 'budget', 'low price', 'economical', 'deal'],
  premium: ['premium', 'luxury', 'high-end', 'best', 'quality', 'expensive'],
};

const emotionKeywords = {
  sensitive: ['sensitive', 'allergy', 'allergic', 'irritation', 'eczema', 'dry'],
  oily: ['oily', 'greasy', 'acne', 'pimple', 'breakout'],
  dry: ['dry', 'dehydrated', 'flaky', 'itchy'],
  combination: ['combination', 'mixed'],
};

const lifestyleKeywords = {
  active: ['active', 'gym', 'fitness', 'sport', 'athlete', 'exercise', 'workout'],
  busy: ['busy', 'quick', 'fast', 'convenient', 'easy'],
  minimal: ['minimal', 'simplify', 'declutter', 'less', 'simple'],
  family: ['family', 'kids', 'children', 'household'],
  travel: ['travel', 'portable', 'compact', 'on-the-go'],
};

/**
 * Extract keywords from user input using NLP techniques
 */
export const extractKeywords = (userInput) => {
  const lowercaseInput = userInput.toLowerCase();
  const extractedKeywords = {
    categories: [],
    attributes: [],
    emotions: [],
    lifestyle: [],
    priceRange: null,
    confidence: 0
  };

  let matchCount = 0;

  // Extract category keywords
  Object.entries(keywordMappings).forEach(([category, keywords]) => {
    keywords.forEach(keyword => {
      if (lowercaseInput.includes(keyword)) {
        extractedKeywords.categories.push(category);
        matchCount++;
      }
    });
  });

  // Extract emotional/skin-related keywords
  Object.entries(emotionKeywords).forEach(([emotion, keywords]) => {
    keywords.forEach(keyword => {
      if (lowercaseInput.includes(keyword)) {
        extractedKeywords.emotions.push(emotion);
        matchCount++;
      }
    });
  });

  // Extract lifestyle keywords
  Object.entries(lifestyleKeywords).forEach(([lifestyle, keywords]) => {
    keywords.forEach(keyword => {
      if (lowercaseInput.includes(keyword)) {
        extractedKeywords.lifestyle.push(lifestyle);
        matchCount++;
      }
    });
  });

  // Detect price preferences
  if (lowercaseInput.includes('budget') || lowercaseInput.includes('cheap') || lowercaseInput.includes('affordable')) {
    extractedKeywords.priceRange = 'budget';
  } else if (lowercaseInput.includes('premium') || lowercaseInput.includes('luxury') || lowercaseInput.includes('expensive')) {
    extractedKeywords.priceRange = 'premium';
  }

  // Remove duplicates
  extractedKeywords.categories = [...new Set(extractedKeywords.categories)];
  extractedKeywords.emotions = [...new Set(extractedKeywords.emotions)];
  extractedKeywords.lifestyle = [...new Set(extractedKeywords.lifestyle)];

  // Calculate confidence score based on keyword matches
  extractedKeywords.confidence = Math.min(matchCount * 0.2, 1); // Max 1.0, 0.2 per match

  return extractedKeywords;
};

/**
 * Calculate relevance score for a product based on user input
 */
export const calculateProductScore = (product, userInput, keywords) => {
  let score = 0;
  const lowercaseInput = userInput.toLowerCase();

  // Direct name/description match (high weight)
  if (product.name && product.name.toLowerCase().includes(lowercaseInput)) {
    score += 100;
  }
  if (product.short_description && product.short_description.toLowerCase().includes(lowercaseInput)) {
    score += 50;
  }

  // Category matches
  keywords.categories.forEach(cat => {
    if (product.category && product.category.toLowerCase().includes(cat)) {
      score += 30;
    }
    if (product.category_name && product.category_name.toLowerCase().includes(cat)) {
      score += 30;
    }
  });

  // Sustainability attributes
  if (keywords.attributes.includes('plastic_free') && product.eco_rating >= 4) {
    score += 25;
  }
  if (keywords.attributes.includes('organic') && product.name.toLowerCase().includes('organic')) {
    score += 20;
  }
  if (keywords.attributes.includes('vegan') && product.name.toLowerCase().includes('vegan')) {
    score += 20;
  }

  // EcoScore preference
  if (product.ecoscore_grade) {
    const gradeScore = { 'A': 40, 'B': 30, 'C': 20, 'D': 10, 'E': 5 };
    score += gradeScore[product.ecoscore_grade] || 10;
  } else if (product.eco_rating) {
    score += product.eco_rating * 8; // 0-40 points
  }

  // Lifestyle match
  if (keywords.lifestyle.includes('travel') && 
      (product.name.toLowerCase().includes('portable') || 
       product.name.toLowerCase().includes('compact'))) {
    score += 15;
  }

  if (keywords.lifestyle.includes('busy') && 
      (product.name.toLowerCase().includes('easy') || 
       product.name.toLowerCase().includes('quick'))) {
    score += 10;
  }

  // Price range preference
  if (product.price && keywords.priceRange) {
    if (keywords.priceRange === 'budget' && product.price < 500) {
      score += 15;
    } else if (keywords.priceRange === 'premium' && product.price > 1000) {
      score += 15;
    }
  }

  // Popularity/rating boost
  if (product.rating) {
    score += Math.min(product.rating * 5, 25); // Up to 25 points for rating
  }

  return score;
};

/**
 * Get smart recommendations based on user query
 */
export const getSmartRecommendations = (userInput, products) => {
  if (!userInput || !products || !Array.isArray(products)) {
    return [];
  }

  // Extract keywords using NLP
  const keywords = extractKeywords(userInput);

  // Score all products
  const scoredProducts = products.map(product => ({
    product,
    score: calculateProductScore(product, userInput, keywords),
    keyword: keywords
  }));

  // Filter out zero-score products and sort by score
  const recommendations = scoredProducts
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(item => item.product);

  // If no matches found, return top-rated eco products
  if (recommendations.length === 0) {
    return products
      .sort((a, b) => {
        const bScore = (b.ecoscore_grade === 'A' ? 5 : 
                       b.ecoscore_grade === 'B' ? 4 : 
                       b.ecoscore_grade === 'C' ? 3 : 2) + (b.rating || 0);
        const aScore = (a.ecoscore_grade === 'A' ? 5 : 
                       a.ecoscore_grade === 'B' ? 4 : 
                       a.ecoscore_grade === 'C' ? 3 : 2) + (a.rating || 0);
        return bScore - aScore;
      })
      .slice(0, 6);
  }

  return recommendations.slice(0, 8); // Return top 8 recommendations
};

/**
 * Get personalized recommendation message based on keywords
 */
export const getRecommendationMessage = (keywords) => {
  const messageParts = [];

  if (keywords.categories.length > 0) {
    messageParts.push(`eco-friendly ${keywords.categories[0]} products`);
  }

  if (keywords.emotions.length > 0) {
    messageParts.push(`suitable for ${keywords.emotions.join(', ')} conditions`);
  }

  if (keywords.lifestyle.length > 0) {
    messageParts.push(`perfect for ${keywords.lifestyle.join(', ')} lifestyle`);
  }

  if (messageParts.length === 0) {
    return 'top-rated eco-friendly products';
  }

  return messageParts.join(', ');
};

/**
 * Calculate similarity between two strings using Levenshtein distance
 */
export const stringSimilarity = (str1, str2) => {
  const s1 = str1.toLowerCase();
  const s2 = str2.toLowerCase();

  if (s1 === s2) return 1;
  if (s1.length === 0 || s2.length === 0) return 0;

  const maxLength = Math.max(s1.length, s2.length);
  const distance = levenshteinDistance(s1, s2);

  return 1 - distance / maxLength;
};

/**
 * Levenshtein distance for string similarity
 */
const levenshteinDistance = (str1, str2) => {
  const matrix = [];

  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[str2.length][str1.length];
};

/**
 * Batch process recommendations for multiple queries
 */
export const getBatchRecommendations = (userQueries, products) => {
  return userQueries.map(query => ({
    query,
    recommendations: getSmartRecommendations(query, products)
  }));
};
