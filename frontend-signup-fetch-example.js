// Example fetch usage for signup form submission

async function handleSignup(event) {
  event.preventDefault();

  const name = event.target.name.value;
  const email = event.target.email.value;
  const password = event.target.password.value;

  try {
    const response = await fetch('http://127.0.0.1:8000/api/signup/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      alert('Signup successful! You can now log in.');
      // Redirect or clear form as needed
    } else {
      alert('Signup failed: ' + data.error);
    }
  } catch (error) {
    alert('An error occurred: ' + error.message);
  }
}

// Attach this handler to your signup form's onSubmit event
// <form onSubmit={handleSignup}>...</form>
