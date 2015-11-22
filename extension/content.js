smenu = document.getElementsByClassName("js-select-button")[0];
var btn = document.createElement("button");
btn.innerHTML = 'Add a Bounty';
btn.onclick = function(){
	window.location = "http://coderbounty.com/post/?url=" + location.protocol+'//'+location.host+location.pathname;
};
btn.style.background='#9A8C76'
btn.style.color='#FFF'
btn.className = "btn";

smenu.parentNode.parentNode.appendChild(btn);