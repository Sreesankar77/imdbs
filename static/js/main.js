document.addEventListener('DOMContentLoaded', ()=>{
  // Optimize role box selection
  const boxes = document.querySelectorAll('.role-box');
  const roleInput = document.getElementById('role-input');
  const createForm = document.getElementById('create-user-form');
  
  // Use event delegation instead of adding listeners to each box
  if(boxes.length > 0) {
    const parent = boxes[0].parentElement;
    parent.addEventListener('click', (e)=>{
      const clickedBox = e.target.closest('.role-box');
      if(!clickedBox) return;
      
      boxes.forEach(x=>x.classList.remove('active'));
      clickedBox.classList.add('active');
      roleInput.value = clickedBox.dataset.role;
      if(clickedBox.dataset.role==='user') createForm?.classList.remove('hidden');
      else createForm?.classList.add('hidden');
    });
    
    // Set default active on load
    const defaultBox = document.getElementById('admin-box');
    if(defaultBox) defaultBox.classList.add('active');
  }
  
  // Dropdown management - single event listener with delegation
  const dropdown = document.querySelector('.dropdown');
  if(dropdown){
    const dropbtn = dropdown.querySelector('.dropbtn');
    const content = dropdown.querySelector('.dropdown-content');
    
    dropbtn?.addEventListener('click', (e)=>{
      e.stopPropagation();
      dropdown.classList.toggle('open');
    });
    
    // Close dropdown when outside is clicked
    document.addEventListener('click', (e)=>{
      if(!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
      }
    }, {capture: false});
  }

  // Search functionality - optimized
  const topbar = document.getElementById('topbar');
  const searchBtn = document.querySelector('.btn.search');
  const searchBox = document.getElementById('searchbox');
  const searchForm = document.getElementById('search-form');
  
  if(searchBtn && topbar && searchBox){
    let searchTimeout;
    
    searchBtn.addEventListener('click', (e)=>{
      e.stopPropagation();
      const isOpen = topbar.classList.contains('search-open');
      
      if(!isOpen){
        topbar.classList.add('search-open');
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(()=>{ searchBox.focus() }, 150);
      } else if(searchBox.value.trim().length > 0){
        searchForm.submit();
      } else {
        topbar.classList.remove('search-open');
      }
    });
    
    // Submit on Enter
    searchBox.addEventListener('keydown', (e)=>{
      if(e.key === 'Enter' && searchBox.value.trim().length > 0){
        e.preventDefault();
        searchForm.submit();
      }
    });
    
    // Close search when clicking outside
    document.addEventListener('click', (e)=>{
      if(topbar.classList.contains('search-open') && !topbar.contains(e.target)){
        topbar.classList.remove('search-open');
      }
    });
  }

  // Clean up form elements on non-detail pages (lazily)
  try{
    const path = window.location.pathname || '';
    const onMovie = /^\/movie\/.+/.test(path);
    if(!onMovie){
      // Use event delegation for better performance if cards exist
      const movieCards = document.querySelectorAll('.card form');
      movieCards.forEach(f=>{
        const action = f.getAttribute('action') || '';
        if(action.includes('/add_to_watchlist') || action.includes('/mark_watched') || action.includes('/add_fav')){
          f.remove();
        }
      });
    }
  }catch(e){console.error('Form cleanup error:', e)}
});
