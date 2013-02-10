$(document).ready(function(){


	$('.user').popover({
		content: "<ul class='nav nav-pills nav-stacked'><li><a href='/logout'>Log Out</a></li><li><a href='/profile'>Edit Profile</a></li></ul>",
		trigger: "hover",
		placement: 'bottom',
		delay: {
			show: 0,
			hide: 2000
		}
	});

	 $(function() { 
        $('.photos').popover('show');
        setTimeout(function(){$(".photos").popover('hide')}, 8000);

      });


	$('.content hr').first().hide();

	$('.button').click(function(e) {
		e.preventDefault();
	});


	$('.postError').hide();

	$('#addPost').click(function(event){
		event.preventDefault();
		if ($("#content").val() === ""){
			$('.control-group').addClass("error");
			$('.postError').show();
		}else{
			var content = escape($('#content').val())
			var data = 'content=' +  content;


			$.ajax({
				type: "POST",
				url: '/post',
				data: data,
				success: function(response){
					$('#content').val('');
					$('.content hr').first().show();
					$('.content').prepend(response);
					$('.content hr').first().hide();
					$('.post').first().animate({
						backgroundColor: "#70cffe"
					}, 1);
					$('.post').first().animate({
						backgroundColor: '#F5F5F5'
					}, 5000);
				}
			});
		}
	});

	$('.deletePost').live('click', function(){
		id = this.id;
		data = {'id': id, 'type': 'post'};
		$.ajax({
			type: "GET",
			url: '/delete',
			data: data,
			success: function(){
				$('.' + id).remove();
				$('.content hr').first().hide();

			}
		});
	});

	$('.deleteComment').live('click', function(){
		id = this.id;
		data = {'id': id, 'type': 'comment'};
		$.ajax({
			type: "GET",
			url: '/delete',
			data: data,
			success: function(){
				$('#' + id).remove();
				$('.clear.' + id).remove();
				// $('.content hr').first().hide();
			}
		});
	});


	$('.left .addComment').live('click', function(){
		$('.commentBox').remove();
		$('.postComment').remove();
		$('.left .addComment').show();
		id = this.id;
		$('.icon1').show();
		html = "<div class='control-group comment'><textarea class='commentBox " + id + "'></textarea><button id='"+ id + "' class='btn btn-small btn-success postComment'>Add Comment</button></div>";
		$('.post.' + id + ' .clear').last().before(html);
		$(".commentBox").css('overflow', 'hidden').autogrow().focus();
		$(this).hide();
		$('.icon1.' + id).hide();
	});

	$('.postComment').live('click', function(){
		id = this.id;
		box = $('.commentBox.' + id);
		if ($(box).val() === ''){
			$('.control-group.comment').addClass("error");
		}else{
			content = box.val();
			data = {'content': content, 'id': id};
			$.ajax({
				type: 'POST',
				url: '/addcomment',
				data: data,
				success: function(content){
					if (content === 'ERROR'){
						window.location.href = "/"
					}else{
						box.val('');
						box.remove();
						$('.postComment').hide();
						$('.icon1').show();
						$('.left .addComment').show();
						$('.post.' + id).append(content);
					}
				}
			});
		}
	});


	$('.applaude').live('click', function(){
		idpost = this.id
		data = {'id': this.id};
		$.ajax({
			type: "POST",
			url: '/applaud',
			data: data,
			success: function(response){
				if (response === '1'){
					$('.' + idpost + '.numberApplauded').html(response + " person applauded")
				}else if (response === 'ERROR'){
					$('.' + idpost + '.numberApplauded').html('You have already applauded this post.')
				}else{
					$('.' + idpost + '.numberApplauded').html(response + " people applauded")
				}
			}

		})
	});


	$('.uploadPhotos').click(function(){
		window.location.href = '/upload'
	})

	$('.loginButton').click(function(){
		window.location.href ='/login';
	})

	$('.registerButton').click(function(){
		window.location.href='/register'
	})





});