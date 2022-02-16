$(document).ready(function() {

    $(document).on('click', '#remove_account', function() {
        var account_id = $(this).attr('account_id');

        req = $.ajax({
            url : '/remove_account',
            type : 'POST',
            data : { account_id : account_id }
        });

        req.done(function(data) {

            if (data['success'] == true){
                //remove channel from front end
                $("#"+account_id).remove();

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


});