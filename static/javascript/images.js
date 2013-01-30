$(document).ready(function(){
	$('.item').first().addClass('active');
	$('.carousel').carousel();

	$('.row img').click(function(){
		itemclass = $(this).attr('class').split(" ")[1];
		// alert(itemclass)
		$('.item.active').removeClass('active')
		$('.item.' + itemclass).addClass('active')
	})

	$('.addPhotos').click(function(){
		window.location.href = '/upload'
	})

	$('.nextpage').click(function(){
		url = document.URL;
		start = url.search('/photos/');
		url = url.substr(start + 8);
		url = parseInt(url) + 1

		window.location.href = '/photos/' + url;
	})
})