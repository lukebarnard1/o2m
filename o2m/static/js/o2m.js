o2m = new Object();

o2m.update_friend = function (friend_id, data, callback) {
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

o2m.set_my_user_photo = function (content) {
	function done(response) {
		window.location = '/o2m/timeline'
	}
	o2m.update_friend(o2m.me.id, {'photo_content_id':content.id}, done)
}

o2m.upload_new_display_picture = function () {
	this.select_content_form.select_content(this.set_my_user_photo, 'image/jpeg')
}

o2m.select_content_form = function() {
	set_selected = function (content) {
		$('#file_name').val(content.file_path)
		$('#select_content').data('content', content)
		$('#existing a').removeClass("active")
		$('#existing').find('#' + content.id + " a").addClass("active")
	}

	content_added = function (response) {
		$('.btn.btn-success').val('Uploaded')
		content = JSON.parse(response)
		refresh_existing()
		set_selected(content)
	}

	html_content_link = function (content) {
		icon = $(document.createElement('div'))
		icon.addClass('content_link').addClass('col-xs-6').addClass('col-md-3')
		icon.attr('id', content.id)

		link = $(document.createElement('a'))
		link.attr('href', 'javascript:;')
		link.on('click', function(){
			set_selected(content)
		})
		link.addClass("thumbnail")

		last_dot_index = content.file_path.lastIndexOf('.') + 1
		content_file_type = content.file_path.substring(last_dot_index).toLowerCase()

		img = document.createElement('img')

		if (content_file_type in {'jpeg': 1, 'jpg': 1, 'png': 1}) {
			img.src = '/content/' + content.id
		} else {
			img.src = '/extra/img/thumbnails/document.png'
		}

		$(img).addClass('img-responsive')

		file_name = document.createElement('p')
		last_slash_index = content.file_path.lastIndexOf('/') + 1
		file_name.innerHTML = content.file_path.substring(last_slash_index)

		link.append(img)
		link.append(file_name)

		icon.append(link)

		return icon
	}

	populate_existing = function (response) {
		existing = JSON.parse(response)

		if (existing.length > 0) {
			$("#existing").html("")
			for (i = 0; i < existing.length; i++) {
				$("#existing").append(html_content_link(existing[i]))
			}
			$("#existing").addClass("active")
			$("#tab_existing").addClass("active")
			$("#upload").removeClass("active")
			$("#tab_upload").removeClass("active")
		} else {
			$("#upload").addClass("active")
			$("#tab_upload").addClass("active")
			$("#existing").removeClass("active")
			$("#tab_existing").removeClass("active")
		}
	}

	var select_content_mime_type = undefined

	refresh_existing = function () {
		url = '/content_list'
		console.log(select_content_mime_type)
		if (select_content_mime_type) {
			url = '/content_list/' + select_content_mime_type
		}

		$.ajax({
			url: url,
			type: 'GET',
			cache: false,
			success: populate_existing,
			error: function(response){console.log(response.status)}
		})
	}

	select_content = function(callback, mime_type) {
		select_content_mime_type = mime_type
		refresh_existing()

		$("#select_content").modal('show');
		$("#select_content").on('hide.bs.modal', function(){
			content = $("#select_content").data('content')
			if (content) {
				callback(content)
			}
		});
		$("#file").on('change', function(){
			file_path = $("#file").val()
			last_slash_index = file_path.lastIndexOf('/') + 1
			if (last_slash_index == 0) {
			last_slash_index = file_path.lastIndexOf('\\') + 1
			}
			$("#file_name").val(file_path.substring(last_slash_index))
		})
	}

	ajax_submit_form = function (form, success, error) {
		$.ajax({
			url: form.attr('action'),
			type: form.attr('method'),
			success: success,
			error: error,
			data: new FormData(form[0]),
			cache: false,
			contentType: false,
			processData: false
		})
	}

	add_content_to_server = function (content_add_form) {
		$.ajax({
			url: '/content/',
			type: 'POST',
			success: content_added,
			error: function(response){console.log(response.status)},
			data: new FormData(content_add_form),
			cache: false,
			contentType: false,
			processData: false
		})
	}

	cancel_select_content = function () {
		// 0 means don't send
		$("#select_content").data('content', 0)
		$("#select_content").modal('hide')
	}

	use_selected_content = function () {
		$("#select_content").modal('hide')
	}

	return this;
}();