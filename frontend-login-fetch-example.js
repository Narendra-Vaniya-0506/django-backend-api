// Example fetch usage for login form submission

async function handleLogin(event) {
  event.preventDefault();

  const identifier = event.target.phone_number.value; // Can be phone number or email
  const password = event.target.password.value;

  try {
    const response = await fetch('http://127.0.0.1:8000/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ identifier, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // Store the token in localStorage
      localStorage.setItem('authToken', data.data.token);
      
      // Store user info
      localStorage.setItem('user', JSON.stringify(data.data.user));
      
      alert('Login successful!');
      
      // Redirect to dashboard or home page
      window.location.href = '/dashboard.html'; // Adjust this URL as needed
      
    } else {
      alert('Login failed: ' + data.error);
    }
  } catch (error) {
    alert('An error occurred: ' + error.message);
  }
}

// Attach this handler to your login form's onSubmit event
// <form onSubmit={handleLogin}>...</form>

// Helper function to check if user is logged in
function isLoggedIn() {
  return localStorage.getItem('authToken') !== null;
}

// Helper function to logout
function logout() {
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
  window.location.href = '/login.html'; // Adjust this URL as needed
}

// Helper function to get auth headers for authenticated requests
function getAuthHeaders() {
  const token = localStorage.getItem('authToken');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
  };
}

// Example of making authenticated request
async function fetchUserProfile() {
  if (!isLoggedIn()) {
    window.location.href = '/login.html';
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/api/profile/', {
      method: 'GET',
      headers: getAuthHeaders()
    });

    const data = await response.json();
    
    if (response.ok) {
      setUser(data.data);
    } else {
      // Token might be invalid, redirect to login
      logout();
    }
  } catch (error) {
    console.error('Error fetching profile:', error);
    alert('Error fetching profile. Please login again.');
    logout();
  }
}
