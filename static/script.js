const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const toggleButton = document.getElementById("toggleButton");
const toggleText = document.getElementById("toggleText");
const formTitle = document.getElementById("formTitle");

// Formlar arası geçiş
toggleButton.addEventListener("click", () => {
  const isLoginVisible = !loginForm.classList.contains("hidden");

  if (isLoginVisible) {
    loginForm.classList.add("hidden");
    registerForm.classList.remove("hidden");
    formTitle.textContent = "Kayıt Ol";
    toggleText.textContent = "Zaten hesabın var mı?";
    toggleButton.textContent = "Giriş yap";
  } else {
    registerForm.classList.add("hidden");
    loginForm.classList.remove("hidden");
    formTitle.textContent = "Giriş Yap";
    toggleText.textContent = "Hesabın yok mu?";
    toggleButton.textContent = "Kayıt ol";
  }
});

// LOGIN formu gönderimi
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = loginForm.querySelector('input[type="email"]').value;
  const password = loginForm.querySelector('input[type="password"]').value;

  const response = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();
  alert(data.message);

  if (response.ok) {
    // Admin ise admin paneline, normal kullanıcı ise blog sayfasına yönlendir
    if (data.is_admin) {
      window.location.href = "/admin";
    } else {
      window.location.href = "/blog";
    }
  }
});

// REGISTER formu gönderimi
registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const name = registerForm.querySelector('input[type="text"]').value;
  const email = registerForm.querySelector('input[type="email"]').value;
  const password = registerForm.querySelector('input[type="password"]').value;

  const response = await fetch("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });

  const data = await response.json();
  alert(data.message);

    if (response.ok) {
    // İstersen kayıt başarılıysa otomatik olarak giriş ekranına dön
    alert(data.message);
    registerForm.classList.add("hidden");
    loginForm.classList.remove("hidden");
}});
