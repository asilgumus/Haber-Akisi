// Blog Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
  // Backend'den gelen blog verilerini kullan
  const blogDataElement = document.getElementById('blog-data');
  const blogData = blogDataElement ? JSON.parse(blogDataElement.getAttribute('data-blogs')) : [];
  const blogList = document.getElementById("blogList");

  if (!blogList) return;

  // Blog kartlarını listele
  blogData.forEach((blog, index) => {
    const card = document.createElement("div");
    
    // İlk kart için özel stil (daha büyük)
    if (index === 0) {
      card.className = "card-hover-effect group block bg-slate-800/60 ring-1 ring-white/10 rounded-lg overflow-hidden md:col-span-2";
      card.innerHTML = `
        <div class="md:flex">
          <div class="md:w-1/2">
            ${blog.image_path ? 
              `<img class="h-48 w-full object-cover md:h-full" src="${blog.image_path}" alt="Haber Resmi">` :
              `<div class="h-48 w-full bg-gradient-to-br from-slate-800 via-sky-900/20 to-slate-900 md:h-full"></div>`
            }
          </div>
          <div class="p-6 md:w-1/2 flex flex-col justify-center">
            <span class="text-xs font-bold uppercase text-cyan-400 tracking-wider">${blog.category || 'genel'}</span>
            <h3 class="mt-2 text-2xl font-bold text-white group-hover:text-cyan-400 transition-colors">${blog.title}</h3>
            <p class="mt-3 text-gray-400 text-sm leading-relaxed">${blog.summary}</p>
            <div class="mt-4 text-xs text-gray-500">
              <span>${blog.author_name || 'Bilinmiyor'} • ${(blog.created_at || '').slice(0, 10)}</span>
            </div>
          </div>
        </div>
      `;
    } else {
      // Diğer kartlar için normal stil
      card.className = "card-hover-effect group block bg-slate-800/60 ring-1 ring-white/10 rounded-lg overflow-hidden";
      card.innerHTML = `
        <div>
          ${blog.image_path ? 
            `<img class="h-48 w-full object-cover" src="${blog.image_path}" alt="Haber Resmi">` :
            `<div class="h-48 w-full bg-gradient-to-br from-slate-800 via-sky-900/20 to-slate-900"></div>`
          }
          <div class="p-6">
            <span class="text-xs font-bold uppercase text-cyan-400 tracking-wider">${blog.category || 'genel'}</span>
            <h3 class="mt-2 text-xl font-bold text-white group-hover:text-cyan-400 transition-colors">${blog.title}</h3>
            <p class="mt-3 text-gray-400 text-sm leading-relaxed">${blog.summary}</p>
            <div class="mt-4 text-xs text-gray-500">
              <span>${blog.author_name || 'Bilinmiyor'} • ${(blog.created_at || '').slice(0, 10)}</span>
            </div>
          </div>
        </div>
      `;
    }
    
    blogList.appendChild(card);

    // Kart tıklanınca detay sayfasına yönlendir
    card.addEventListener('click', (e) => {
      e.preventDefault();
      const payload = {
        id: blog.id,
        title: blog.title,
        summary: blog.summary,
        date: blog.created_at.slice(0, 10),
        author: blog.author_name
      };
      try { 
        sessionStorage.setItem('selectedBlog', JSON.stringify(payload)); 
      } catch (_) {}
      window.location.href = `/blogDetail.html/id=${blog.id}`;
    });
  });

  // Eğer blog yoksa mesaj göster
  if (blogData.length === 0) {
    blogList.innerHTML = `
      <div class="col-span-full text-center py-16">
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-300 mb-2">Henüz blog yazısı yok</h3>
        <p class="text-gray-400">İlk blog yazıları yakında eklenecek.</p>
      </div>
    `;
  }

  // Live search functionality
  const searchInput = document.querySelector('input[type="search"]');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      const query = this.value.toLowerCase().trim();
      let filteredBlogs = blogData;
      
      if (query) {
        filteredBlogs = blogData.filter(blog => 
          blog.title.toLowerCase().includes(query) || 
          blog.summary.toLowerCase().includes(query)
        );
      }
      
      // Clear list
      blogList.innerHTML = '';
      
      // Render filtered blogs
      if (filteredBlogs.length > 0) {
        filteredBlogs.forEach((blog, index) => {
          const card = document.createElement("div");
          
          // İlk kart için özel stil (daha büyük)
          if (index === 0) {
            card.className = "card-hover-effect group block bg-slate-800/60 ring-1 ring-white/10 rounded-lg overflow-hidden md:col-span-2";
            card.innerHTML = `
              <div class="md:flex">
                <div class="md:w-1/2">
                  ${blog.image_path ? 
                    `<img class="h-48 w-full object-cover md:h-full" src="${blog.image_path}" alt="Haber Resmi">` :
                    `<div class="h-48 w-full bg-gradient-to-br from-slate-800 via-sky-900/20 to-slate-900 md:h-full"></div>`
                  }
                </div>
                <div class="p-6 md:w-1/2 flex flex-col justify-center">
                  <span class="text-xs font-bold uppercase text-cyan-400 tracking-wider">${blog.category || 'genel'}</span>
                  <h3 class="mt-2 text-2xl font-bold text-white group-hover:text-cyan-400 transition-colors">${blog.title}</h3>
                  <p class="mt-3 text-gray-400 text-sm leading-relaxed">${blog.summary}</p>
                  <div class="mt-4 text-xs text-gray-500">
                    <span>${blog.author_name || 'Bilinmiyor'} • ${(blog.created_at || '').slice(0, 10)}</span>
                  </div>
                </div>
              </div>
            `;
          } else {
            // Diğer kartlar için normal stil
            card.className = "card-hover-effect group block bg-slate-800/60 ring-1 ring-white/10 rounded-lg overflow-hidden";
            card.innerHTML = `
              <div>
                ${blog.image_path ? 
                  `<img class="h-48 w-full object-cover" src="${blog.image_path}" alt="Haber Resmi">` :
                  `<div class="h-48 w-full bg-gradient-to-br from-slate-800 via-sky-900/20 to-slate-900"></div>`
                }
                <div class="p-6">
                  <span class="text-xs font-bold uppercase text-cyan-400 tracking-wider">${blog.category || 'genel'}</span>
                  <h3 class="mt-2 text-xl font-bold text-white group-hover:text-cyan-400 transition-colors">${blog.title}</h3>
                  <p class="mt-3 text-gray-400 text-sm leading-relaxed">${blog.summary}</p>
                  <div class="mt-4 text-xs text-gray-500">
                    <span>${blog.author_name || 'Bilinmiyor'} • ${(blog.created_at || '').slice(0, 10)}</span>
                  </div>
                </div>
              </div>
            `;
          }
          
          blogList.appendChild(card);

          // Kart tıklanınca detay sayfasına yönlendir
          card.addEventListener('click', (e) => {
            e.preventDefault();
            const payload = {
              id: blog.id,
              title: blog.title,
              summary: blog.summary,
              date: blog.created_at.slice(0, 10),
              author: blog.author_name
            };
            try { 
              sessionStorage.setItem('selectedBlog', JSON.stringify(payload)); 
            } catch (_) {}
            window.location.href = `/blogDetail.html/id=${blog.id}`;
          });
        });
        
        // Scroll to the blog list
        blogList.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else if (query) {
        blogList.innerHTML = `
          <div class="col-span-full text-center py-16">
            <div class="text-gray-400 mb-4">
              <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-300 mb-2">Arama sonucu bulunamadı</h3>
            <p class="text-gray-400">Başka bir arama terimi deneyin.</p>
          </div>
        `;
      }
    });
  }
});
