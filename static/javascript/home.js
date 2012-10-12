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
			var data = 'content=' +  $('#content').val();


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
		html = "<div class='control-group comment'><textarea class='commentBox " + id + "'></textarea><button id='"+ id + "' class='btn btn-small btn-success postComment'>Add Comment</button></div>";
		$('.post.' + id + ' .clear').last().before(html);
		$(".commentBox").css('overflow', 'hidden').autogrow().focus();
		$(this).hide();
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
						$('.left .addComment').show();
						$('.post.' + id).append(content);
					}
				}
			});
		}
	});

	












});