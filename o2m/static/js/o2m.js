o2m = (function(){

	update_friend = function (friend_id, data, callback) {
		if(!callback) {
			callback = function(response){console.log(response.status)}
		}
		
		$.ajax({
			url: '/friend/' + friend_id,
			type: 'PUT',
			success: callback,
			data: JSON.stringify(data),
			error: function(response){console.log(response.status)}
		})
	}

	set_my_user_photo = function (content) {
		function done(response) {
			window.location = '/o2m/timeline'
		}
		update_friend('{{me.id}}', {'photo_content_id':content.id}, done)
	}

	upload_new_display_picture = function () {
		select_content(set_my_user_photo, 'image/jpeg')
	}

	return this;
})();