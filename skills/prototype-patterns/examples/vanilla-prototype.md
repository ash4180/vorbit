# Vanilla HTML/CSS Prototype Example

## Scenario

Prototyping a login form without a framework.

## Generated Files

### `prototype/login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login Prototype</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #f5f5f5;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .card {
      background: white;
      padding: 2rem;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      width: 100%;
      max-width: 400px;
    }

    h1 {
      margin-bottom: 1.5rem;
      font-size: 1.5rem;
    }

    .form-group {
      margin-bottom: 1rem;
    }

    label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
    }

    input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 1rem;
    }

    input:focus {
      outline: none;
      border-color: #3b82f6;
    }

    .btn {
      width: 100%;
      padding: 0.75rem;
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 1rem;
      cursor: pointer;
    }

    .btn:hover {
      background: #2563eb;
    }

    .error {
      color: #dc2626;
      font-size: 0.875rem;
      margin-top: 0.5rem;
      display: none;
    }

    .error.show {
      display: block;
    }

    .success {
      text-align: center;
      color: #16a34a;
      display: none;
    }

    .success.show {
      display: block;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Login</h1>

    <form id="loginForm">
      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" placeholder="you@example.com" required>
        <div class="error" id="emailError">Please enter a valid email</div>
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" placeholder="••••••••" required>
        <div class="error" id="passwordError">Password must be 8+ characters</div>
      </div>

      <div class="error" id="formError">Invalid email or password</div>

      <button type="submit" class="btn">Log In</button>
    </form>

    <div class="success" id="success">
      <h2>Login successful!</h2>
      <p>Redirecting to dashboard...</p>
    </div>
  </div>

  <script>
    // Mock response - matches POST /api/auth/login
    const MOCK_RESPONSES = {
      success: { token: 'mock-jwt-token', user: { id: 1, email: 'test@example.com' } },
      invalidCredentials: { error: 'Invalid email or password' },
      validationError: { errors: { email: 'Invalid format', password: 'Too short' } }
    };

    // Mock valid credentials
    const VALID_CREDENTIALS = {
      email: 'test@example.com',
      password: 'password123'
    };

    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Reset errors
      document.querySelectorAll('.error').forEach(el => el.classList.remove('show'));

      const email = emailInput.value;
      const password = passwordInput.value;

      // Client-side validation
      let hasError = false;

      if (!email.includes('@')) {
        document.getElementById('emailError').classList.add('show');
        hasError = true;
      }

      if (password.length < 8) {
        document.getElementById('passwordError').classList.add('show');
        hasError = true;
      }

      if (hasError) return;

      // Simulate API call
      // TODO: Replace with real fetch('/api/auth/login', { ... })
      const response = await simulateLogin(email, password);

      if (response.error) {
        document.getElementById('formError').textContent = response.error;
        document.getElementById('formError').classList.add('show');
      } else {
        form.style.display = 'none';
        document.getElementById('success').classList.add('show');
        // TODO: Store token, redirect
        console.log('Token:', response.token);
      }
    });

    // Mock API function - remove when connecting real API
    function simulateLogin(email, password) {
      return new Promise(resolve => {
        setTimeout(() => {
          if (email === VALID_CREDENTIALS.email && password === VALID_CREDENTIALS.password) {
            resolve(MOCK_RESPONSES.success);
          } else {
            resolve(MOCK_RESPONSES.invalidCredentials);
          }
        }, 500);
      });
    }
  </script>
</body>
</html>
```

## Key Points

1. **Single file** - HTML, CSS, JS all in one for simplicity
2. **No dependencies** - Works by opening file in browser
3. **Mock function** - `simulateLogin()` simulates API delay
4. **Easy swap** - Replace `simulateLogin` with real `fetch()`
5. **Multiple states** - Shows validation, API error, success

## How to Swap to Real API

```diff
- // Mock API function - remove when connecting real API
- function simulateLogin(email, password) { ... }

+ async function login(email, password) {
+   const response = await fetch('/api/auth/login', {
+     method: 'POST',
+     headers: { 'Content-Type': 'application/json' },
+     body: JSON.stringify({ email, password })
+   });
+   return response.json();
+ }

- const response = await simulateLogin(email, password);
+ const response = await login(email, password);
```
