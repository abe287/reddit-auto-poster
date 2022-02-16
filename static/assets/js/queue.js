$(document).ready(function() {
    $(document).on('click', '#text_schedule_button', function() {
        var text_title = $('#text_title').val();
        var text_body = $('#text_body').val();
        var text_date = $('#text_date').val();
        var text_time = $('#text_time').val();
        var text_account = $('#text_account').val();
        var text_subreddit = $('#text_subreddit').val();
        
        var data = {
            "post_type": "text",
            "text_title" : text_title, 
            "text_body" : text_body, 
            "text_date" : text_date, 
            "text_time" : text_time, 
            "text_subreddit" : text_subreddit,
            "text_account": text_account
        }

        var form_data = new FormData();
        form_data.append('data', JSON.stringify(data));
        
        req = $.ajax({
            url : '/schedule_post',
            type : 'POST',
            data : form_data,
            contentType: false,
            processData: false,
            cache: false
        });
        
        $("#text_schedule_button").replaceWith('<button id="text_schedule_button" type="button" class="btn btn-primary" disabled><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Uploading...</button>');

        req.done(function(data) {        
            $("#text_schedule_button").replaceWith('<button id="text_schedule_button" type="button" class="btn btn-primary">Schedule</button>')    
            if (data['success'] == true){
                //delete initial post disclaimer (if still on page)
                if ($('#post_disclaimer').length) {
                    $('#post_disclaimer').replaceWith(
                        `<div class="row" id="header_buttons">
                            <div class="col-sm-12">
                                <h5 class="float-left p-1"><b>Scheduled Posts</b></h5>
                                <p class="float-right">
                                    <button class="btn btn-primary" data-toggle="modal" data-target="#scheduleTextPost">Schedule Text</button>
                                    <button class="btn btn-primary" data-toggle="modal" data-target="#scheduleMediaPost">Schedule Media</button>
                                </p>
                            </div>
                        </div>
                        <div id="post_container" class="row">
                        </div>
                        `
                    );

                }

                //render html
                post_html = `<div id="`+data['post_details']['_id']['$oid']+`" class="col-sm-12 mb-2">
                            <div class="card bg-dark text-white">
                                <div class="card-body">
                                    <h5 class="card-title">`+data['post_details']['title']+`</h5>

                                    <p class="card-text">`+data['post_details']['body']+`</p>

                                    <button post_id="`+data['post_details']['_id']['$oid']+`" id="remove_post" class="btn btn-danger">Remove Post</button>
                                    <button post_id="`+data['post_details']['_id']['$oid']+`" id="edit_post" class="btn btn-white" data-toggle="modal" data-target="#updatePost">Edit Post</button>

                                    <span class="float-right badge badge-secondary m-1">`+data['post_details']['string_timestamp']+`</span>
                                    <span class="float-right badge badge-secondary m-1">r/`+data['post_details']['subreddit']+`</span>
                                    <span class="float-right badge badge-secondary m-1">u/`+data['post_details']['account_username']+`</span>
                                </div>
                            </div>
                        </div>`
                $("#post_container").append(post_html)

                //close modal and clear values
                $('#scheduleTextPost').modal('hide');
                $('#text_title').val('');
                $('#text_body').val('');
                $('#text_date').val('');
                $('#text_time').val('');
                $('#text_subreddit').val('');

                //success pop up
                Swal.fire({
                    title: 'Success',
                    text: data['message'],
                    icon: 'success'
                })
                
            }
            else{
                Swal.fire({
                    title: 'Error',
                    text: data['message'],
                    icon: 'error'
                })
            }

        });

    });

    $(document).on('click', '#media_schedule_button', function() {
        var media_title = $('#media_title').val();
        var file_data = $('#media_post_file').prop('files')[0];
        var form_data = new FormData();
        form_data.append('file', file_data);
        var media_date = $('#media_date').val();
        var media_time = $('#media_time').val();
        var media_account = $('#media_account').val();
        var media_subreddit = $('#media_subreddit').val();
        
        var data = {
            "post_type": "media",
            "media_title" : media_title, 
            "media_date" : media_date, 
            "media_time" : media_time, 
            "media_subreddit" : media_subreddit,
            "media_account": media_account
        }
        
        form_data.append('data', JSON.stringify(data));
        
        if (file_data.size < 210763776) {
            req = $.ajax({
                url : '/schedule_post',
                type : 'POST',
                data : form_data,
                credentials : "include",
                contentType: false,
                processData: false,
                cache: false
            });

            $("#media_schedule_button").replaceWith('<button id="media_schedule_button" type="button" class="btn btn-primary" disabled><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Uploading...</button>');


            req.done(function(data) {
                //replace button with default
                $("#media_schedule_button").replaceWith('<button id="media_schedule_button" type="button" class="btn btn-primary">Schedule</button>')
    
                if (data['success'] == true){
                    //delete initial post disclaimer (if still on page)
                    if ($('#post_disclaimer').length) {
                        $('#post_disclaimer').replaceWith(
                            `<div class="row" id="header_buttons">
                                <div class="col-sm-12">
                                    <h5 class="float-left p-1"><b>Scheduled Posts</b></h5>
                                    <p class="float-right">
                                        <button class="btn btn-primary" data-toggle="modal" data-target="#scheduleTextPost">Schedule Text</button>
                                        <button class="btn btn-primary" data-toggle="modal" data-target="#scheduleMediaPost">Schedule Media</button>
                                    </p>
                                </div>
                            </div>
                            <div id="post_container" class="row">
                            </div>
                            `
                        );

                    }

                    //render html
                    if (data['post_details']['content_type'] == 'image/png' || data['post_details']['content_type'] == 'image/jpeg'){
                        media_source = '<img class="card-img-top" src="'+ data['post_details']['media_url'] +'" referrerPolicy="no-referrer">'
                    }
                    else{
                        media_source = '<video controls><source src="'+ data['post_details']['media_url'] +'" type="video/mp4"></video>'
                    }
                    post_html = `
                                <div id="`+data['post_details']['_id']['$oid']+`" class="col-sm-12 mb-2">
                                    <div class="card bg-dark text-white">
                                        `+media_source+`
                                        <div class="card-body">
                                            <h5 class="card-title">`+data['post_details']['title']+`</h5>

                                            <button post_id="`+data['post_details']['_id']['$oid']+`" id="remove_post" class="btn btn-danger">Remove Post</button>
                                            <button post_id="`+data['post_details']['_id']['$oid']+`" id="edit_post" class="btn btn-white" data-toggle="modal" data-target="#updatePost">Edit Post</button>

                                            <span class="float-right badge badge-secondary m-1">`+data['post_details']['string_timestamp']+`</span>
                                            <span class="float-right badge badge-secondary m-1">r/`+data['post_details']['subreddit']+`</span>
                                            <span class="float-right badge badge-secondary m-1">u/`+data['post_details']['account_username']+`</span>
                                        </div>
                                    </div>
                                </div>
                                `
                    $("#post_container").append(post_html)

                    //close modal and clear values
                    $('#scheduleMediaPost').modal('hide');
                    $('#media_title').val('');
                    $('#media_date').val('');
                    $('#media_time').val('');
                    $('#media_account').val('');
                    $('#media_subreddit').val('');

                    document.getElementById('media_post_file').value = null;

                    //success pop up
                    Swal.fire({
                        title: 'Success',
                        text: data['message'],
                        icon: 'success'
                    })
                    
                }
                else{
                    Swal.fire({
                        title: 'Error',
                        text: data['message'],
                        icon: 'error'
                    })
                }

            });
        }
        
        else{
            Swal.fire({
                title: 'Error',
                text: "Select a file less than 200 MB.",
                icon: 'error'
            })
        }
    });

    $(document).on('click', '#remove_post', function() {
        var post_id = $(this).attr('post_id');
        
        req = $.ajax({
            url : '/remove_post',
            type : 'POST',
            data : { post_id : post_id },
            credentials : "include"
        });
        
        req.done(function(data) {
            if (data['success'] == true){
                //remove html
                $("#"+post_id).remove()

                //if no scheuled posts on page show post_disclaimer
                if ($("#post_container").children().length == 0){
                    $("#header_buttons").replaceWith(
                        `
                        <main id="post_disclaimer" role="main">
                        <div class="jumbotron bg-dark text-white">
                          <div class="col-sm-8 mx-auto">
                            <h1>No scheduled posts</h1>
                            <p>You currently have no posts scheduled for posting. Add some by clicking on the button below.</p>
                            <p>Please make sure to link your reddit account before attempting to schedule a post. If you have not linked your account already please do so by going to <a href="/accounts">accounts</a>.</p>
                            <p>
                              <button class="btn btn-primary" data-toggle="modal" data-target="#scheduleTextPost">Schedule Text</button>
                              <button class="btn btn-primary" data-toggle="modal" data-target="#scheduleMediaPost">Schedule Media</button>
                            </p>
                          </div>
                        </div>
                      </main>
                        `
                    )
                    $("#post_container").remove()
                }

                //success pop up
                Swal.fire({
                    title: 'Success',
                    text: data['message'],
                    icon: 'success'
                })
                
            }
            else{
                Swal.fire({
                    title: 'Error',
                    text: data['message'],
                    icon: 'error'
                })
            }

        });

    });

    $(document).on('click', '#edit_post', function() {
        var post_id = $(this).attr('post_id');
        
        req = $.ajax({
            url : '/edit_post',
            type : 'POST',
            data : { post_id : post_id },
            credentials : "include"
        });
        

        req.done(function(data) {
            if (data['success'] == true){
                //render modal html for post
                accounts_html = '<option selected value="'+data['post']['account_id']+'">'+data['post']['account_username']+'</option>';
                for(var i=0; i<data['accounts'].length; i++){
                    if (data['post']['account_id'] != data['accounts'][i]['_id']['$oid']){
                        accounts_html += '<option value="'+data['accounts'][i]['_id']['$oid']+'">'+data['accounts'][i]['username']+'</option>';
                    }
                }

                if (data['post']['post_type'] == "text"){
                    $("#update_post_content").html(
                        `
                            <div class="modal-header">
                                <h5 class="modal-title" id="exampleModalLongTitle">Schedule Text Post</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                            </div>
                            <div class="modal-body p-4">
                                <div class="form-group">
                                    <label>Title</label>
                                    <input id="update_title" class="form-control" placeholder="Post Title" value="`+data['post']['title']+`">
                                </div>
                
                                <div class="form-group">
                                    <label>Post body</label>
                                    <textarea id="update_text_body" class="form-control" rows="7" style="resize: none" value="`+data['post']['raw_body']+`">`+data['post']['raw_body']+`</textarea>
                                </div>
                
                                <div class="form-group">
                                    <label>Subreddit</label>
                                    <input id="update_subreddit" class="form-control" placeholder="subreddit" value="`+data['post']['subreddit']+`">
                                </div>
                
                                <div class="form-group">
                                    <div class="form-row">
                                        <div class="col">
                                            <label>Date</label>
                                            <input id="update_date" type="text" class="form-control" placeholder="01/01/2000" value="`+data['post']['raw_date']+`">
                                        </div>
                                        <div class="col">
                                            <label>Time</label>
                                            <input id="update_time" type="text" class="form-control" placeholder="01:00 PM" value="`+data['post']['raw_time']+`">
                                        </div>
                                    </div>
                                </div>
                
                                <div class="form-group">
                                    <label>Account</label>
                                    <select class="form-control" id="update_account">`+accounts_html+`</select>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                                <button post_id="`+data['post']['_id']['$oid']+`" id="update_button" type="button" class="btn btn-primary">Update</button>
                            </div>
                        `
                    );
                }
                else{
                    $("#update_post_content").html(
                        `
                            <div class="modal-header">
                                <h5 class="modal-title" id="exampleModalLongTitle">Schedule Media Post</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                            </div>
                            <div class="modal-body p-4">
                                <div class="form-group">
                                    <label>Title</label>
                                    <input id="update_title" class="form-control" placeholder="Post Title" value="`+data['post']['title']+`">
                                </div>
                
                                <div class="form-group">
                                    <label>Media File</label>
                                    <div class="input-group mb-3">
                                        <div class="input-group-prepend">
                                        <span class="input-group-text">Upload</span>
                                        </div>
                                        <div class="custom-file">
                                        <input id="update_media_post_file" type="file" class="custom-file-input" id="inputGroupFile01">
                                        <label class="custom-file-label" for="inputGroupFile01">Change file</label>
                                        </div>
                                    </div>
                                </div>
                
                                <div class="form-group">
                                    <label>Subreddit</label>
                                    <input id="update_subreddit" class="form-control" placeholder="subreddit" value="`+data['post']['subreddit']+`">
                                </div>
                
                                <div class="form-group">
                                    <div class="form-row">
                                        <div class="col">
                                            <label>Date</label>
                                            <input id="update_date" type="text" class="form-control" placeholder="01/01/2000" value="`+data['post']['raw_date']+`">
                                        </div>
                                        <div class="col">
                                            <label>Time</label>
                                            <input id="update_time" type="text" class="form-control" placeholder="01:00 PM" value="`+data['post']['raw_time']+`">
                                        </div>
                                    </div>
                                </div>
                
                                <div class="form-group">
                                    <label>Account</label>
                                    <select class="form-control" id="update_account">`+accounts_html+`</select>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                                <button post_id="`+data['post']['_id']['$oid']+`" id="update_button" type="button" class="btn btn-primary">Update</button>
                            </div>
                        `
                    );
                }           

            }
            else{
                console.log("error fetching post data");
            }

        });

    });

    $(document).on('click', '#update_button', function() {
        data = {
            "post_id": $(this).attr('post_id'),
            "update_title": $('#update_title').val(),
            "update_time": $('#update_time').val(),
            "update_date": $('#update_date').val(),
            "update_subreddit": $('#update_subreddit').val(),
            "update_account": $('#update_account').val()
        }

        var form_data = new FormData();
        if ( $("#update_media_post_file").length ){
            var file_data = $('#update_media_post_file').prop('files')[0];
            form_data.append('file', file_data);
        }
        if ( $("#update_text_body").length ){
            data.text_post_body = $('#update_text_body').val();
        }
        
        
        form_data.append('data', JSON.stringify(data));
        
        req = $.ajax({
            url : '/update_post',
            type : 'POST',
            data : form_data,
            contentType: false,
            processData: false,
            cache: false
        });

        //replace button with loading button
        $("#update_button").replaceWith('<button id="update_button" type="button" class="btn btn-primary" disabled><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Updating...</button>');
        
        req.done(function(data) {
            //replace button
            $("#update_button").replaceWith('<button id="update_button" type="button" class="btn btn-primary">Update</button>');
            //hide modal
            $('#updatePost').modal('hide');

            if (data['success'] == true){
                //render html for post card
                if (data['post_details']['post_type'] == "text"){
                    $("#"+data['post_details']['_id']['$oid']).replaceWith(
                        `
                        <div id="`+data['post_details']['_id']['$oid']+`" class="col-sm-12 mb-2">
                            <div class="card bg-dark text-white">
                                <div class="card-body">
                                    <h5 class="card-title">`+data['post_details']['title']+`</h5>

                                    <p class="card-text">`+data['post_details']['body']+`</p>

                                    <button post_id="`+data['post_details']['_id']['$oid']+`" id="remove_post" class="btn btn-danger">Remove Post</button>
                                    <button post_id="`+data['post_details']['_id']['$oid']+`" id="edit_post" class="btn btn-white" data-toggle="modal" data-target="#updatePost">Edit Post</button>

                                    <span class="float-right badge badge-secondary m-1">`+data['post_details']['string_timestamp']+`</span>
                                    <span class="float-right badge badge-secondary m-1">r/`+data['post_details']['subreddit']+`</span>
                                    <span class="float-right badge badge-secondary m-1">u/`+data['post_details']['account_username']+`</span>
                                </div>
                            </div>
                        </div>
                        `
                    );
                }
                else{
                    if (data['post_details']['content_type'] == 'image/png' || data['post_details']['content_type'] == 'image/jpeg'){
                        media_source = '<img class="card-img-top" src="'+ data['post_details']['media_url'] +'" referrerPolicy="no-referrer">'
                    }
                    else{
                        media_source = '<video controls><source src="'+ data['post_details']['media_url'] +'" type="video/mp4"></video>'
                    }
                    $("#"+data['post_details']['_id']['$oid']).replaceWith(
                        `
                        <div id="`+data['post_details']['_id']['$oid']+`" class="col-sm-12 mb-2">
                            <div class="card bg-dark text-white">
                                `+media_source+`
                                <div class="card-body">
                                    <h5 class="card-title">`+data['post_details']['title']+`</h5>

                                    <button post_id="`+data['post_details']['_id']['$oid']+`" id="remove_post" class="btn btn-danger">Remove Post</button>
                                    <button post_id="`+data['post_details']['_id']['$oid']+`" id="edit_post" class="btn btn-white" data-toggle="modal" data-target="#updatePost">Edit Post</button>

                                    <span class="float-right badge badge-secondary m-1">`+data['post_details']['string_timestamp']+`</span>
                                    <span class="float-right badge badge-secondary m-1">r/`+data['post_details']['subreddit']+`</span>
                                    <span class="float-right badge badge-secondary m-1">u/`+data['post_details']['account_username']+`</span>
                                </div>
                            </div>
                        </div>
                        `
                    );
                }
                
                //show success pop up
                Swal.fire({
                    title: 'Success',
                    text: data['message'],
                    icon: 'success'
                })

            }
            else{
                Swal.fire({
                    title: 'Error',
                    text: data['message'],
                    icon: 'error'
                })
            }

        });

    });

});