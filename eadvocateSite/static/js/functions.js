/* Javascripts
==================================================
	
	By: Paul Hladun
	paulhladun.com
	2013


// remap jQuery to $
(function($){})(window.jQuery);


/* trigger when page is ready */
$(document).ready(function (){

/* Fade In Entire Page On Load
================================================== */

$(document).ready(function () {
	$('body').hide().delay(475).fadeIn(2275);
	});
});
  
/* Link Scrolling - Internal Links
================================================== */
	$(document).ready(function($) {
		$(".scroll").click(function(event){
		event.preventDefault();
		$('html,body').animate({scrollTop:$(this.hash).offset().top}, 750);
	});
});
	
/* Mobile Menu
================================================== */

		
$(document).ready(function() {  
var stickyNavTop = $('nav').offset().top;  
  
var stickyNav = function(){  
var scrollTop = $(window).scrollTop();  
       
if (scrollTop > stickyNavTop) {   
    $('nav').addClass('stickNav');  
} else {  
    $('nav').removeClass('stickNav');   
}  
};  
  
stickyNav();  
  
$(window).scroll(function() {  
    stickyNav();  
});  
}); 
	
	$(document).ready(function(){
		$('.slideToggler2').click(function(){
			$('.slideContent2').slideToggle('slow');
			$(this).toggleClass('slideSign2');
			return false;
		});
		$('.collaps2').click(function(){
			$('.slideContent2').slideToggle('slow');
			$('.slideToggler2').toggleClass('slideSign2');
			return false;
		});
	});
	
/* optional triggers

$(window).load(function() {
	
});

$(window).resize(function() {
	
});

*/