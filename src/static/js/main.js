document.addEventListener("DOMContentLoaded", () => {

updateYear();

initMobileMenu();

});


function updateYear(){

const year = document.querySelector(".year");

if(year){
year.textContent = new Date().getFullYear();
}

}


function initMobileMenu(){

const toggle = document.getElementById("menuToggle");
const nav = document.getElementById("navMenu");

if(!toggle || !nav) return;

toggle.addEventListener("click", () => {

nav.classList.toggle("active");

});

}