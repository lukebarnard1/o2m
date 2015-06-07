o2m = (function(){

	function update_friend(friend_id, data, callback) {
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

	function set_my_user_photo(content) {
		function done(response) {
			window.location = '/o2m/timeline'
		}
		update_friend('{{me.id}}', {'photo_content_id':content.id}, done)
	}

	function upload_new_display_picture() {
		select_content(set_my_user_photo, 'image/jpeg')
	}

})();