/**
 * Azure authentication and user management for HopSkip application
 */
import { v4 as uuidv4 } from 'uuid';

// Simple user state management
// In production, this would be replaced with Azure AD B2C or similar service
class UserManager {
  constructor() {
    this.listeners = [];
    this.currentUser = null;
    
    // Try to load user from localStorage
    this.initializeUser();
  }

  // Initialize user from localStorage or create anonymous user
  initializeUser() {
    try {
      const savedUser = localStorage.getItem('hopskip_user');
      if (savedUser) {
        this.currentUser = JSON.parse(savedUser);
        this.notifyListeners();
      } else {
        this.createAnonymousUser();
      }
    } catch (error) {
      console.error("Error initializing user:", error);
      this.createAnonymousUser();
    }
  }

  // Create anonymous user with unique ID
  createAnonymousUser() {
    const anonymousUser = {
      uid: uuidv4(),
      isAnonymous: true,
      displayName: "Anonymous User"
    };
    
    this.currentUser = anonymousUser;
    localStorage.setItem('hopskip_user', JSON.stringify(anonymousUser));
    this.notifyListeners();
    
    console.log("Anonymous user created", anonymousUser);
    return anonymousUser;
  }

  // Get current user
  getUser() {
    return this.currentUser;
  }

  // Add listener for user state changes
  addAuthStateListener(callback) {
    this.listeners.push(callback);
    
    // Immediately call with current state
    if (this.currentUser) {
      callback(this.currentUser);
    } else {
      callback(null);
    }
    
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  // Notify all listeners of user state change
  notifyListeners() {
    this.listeners.forEach(listener => {
      listener(this.currentUser);
    });
  }
}

// Create singleton instance
const userManager = new UserManager();

// Export functions that match the interface expected by the app
export const auth = userManager;
export const onAuthStateChanged = userManager.addAuthStateListener.bind(userManager);
