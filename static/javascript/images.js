$(document).ready(function(){
	$('.item').first().addClass('active');
	$('.carousel').carousel();

	$('img').click(function(){
		itemclass = $(this).attr('class').split(" ")[1];
		// alert(itemclass)
		$('.item.active').removeClass('active')
		$('.item.' + itemclass).addClass('active')
	})

	$('.addPhotos').click(function(){
		window.location.href = '/upload'
	})
})