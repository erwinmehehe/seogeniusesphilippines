/* Navigation, project filtering and optional quote context. No form interception. */
(() => {
 const button=document.querySelector('[data-menu-button]');
 const menu=document.querySelector('[data-mobile-nav]');
 const close=()=>{if(!button||!menu)return;button.setAttribute('aria-expanded','false');button.textContent='Menu';menu.hidden=true;menu.classList.remove('open');};
 button?.addEventListener('click',()=>{const open=button.getAttribute('aria-expanded')!=='true';button.setAttribute('aria-expanded',String(open));button.textContent=open?'Close':'Menu';menu.hidden=!open;menu.classList.toggle('open',open);});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&button?.getAttribute('aria-expanded')==='true'){close();button.focus();}});
 menu?.addEventListener('click',e=>{if(e.target.closest('a'))close();});
 const filters=[...document.querySelectorAll('[data-filter]')];
 const cards=[...document.querySelectorAll('[data-topic]')];
 filters.forEach(b=>b.addEventListener('click',()=>{filters.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));cards.forEach(c=>c.classList.toggle('hide',b.dataset.filter!=='All'&&c.dataset.topic!==b.dataset.filter));}));
 const form=document.querySelector('#contact-form');
 if(form){const query=new URLSearchParams(location.search);for(const key of ['audience','plan','service']){const field=form.elements.namedItem(key),value=query.get(key);if(field?.options&&value&&[...field.options].some(o=>o.value===value))field.value=value;}}
})();

// Avoid stacking the fixed call link over the homepage's closing enquiry actions.
const closingEnquiry=document.querySelector('.after-hero .studio-close');
if(closingEnquiry&&'IntersectionObserver' in window){
 const observer=new IntersectionObserver(entries=>{
  document.body.classList.toggle('closing-enquiry-visible',entries[0].isIntersecting);
 },{threshold:0.25});
 observer.observe(closingEnquiry);
}
