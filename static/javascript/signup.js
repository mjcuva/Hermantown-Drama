$(document).ready(function(){

	// var options = {
	// 	beforeSubmit: function(){
	// 		return $('#signupform').validate().form();
	// 	}
	// };

	// $('#signupform').ajaxForm(options);

	$("#signupform").validate({

		rules:{
			user_first: "required",
			user_last: "required",
			user_email: {
				required: true,
				email: true
			},
			user_pass: {
				required: true,
				minlength: 6
			},
			user_verPass: {
				required: true,
				equalTo: '#user_pass'
			}
		},

		messages:{
			user_first:"Enter your first name",
			user_last:"Enter your last name",
			user_email:{
			required:"Enter your email address",
			email:"Enter valid email address"},
			user_pass:{
			required:"Enter your password",
			minlength:"Password must be minimum 6 characters"},
			user_verPass:{
			required:"Enter confirm password",
			equalTo:"Password and Confirm Password must match"},
		},


		errorClass: "help-inline",
		errorElement: "span",
		highlight:function(element, errorClass, validClass)
		{
			$(element).parents('.control-group').addClass('error');
		},
		unhighlight: function(element, errorClass, validClass)
		{
			$(element).parents('.control-group').removeClass('error');
			// $(element).parents('.control-group').addClass('success');
		}

	});
});