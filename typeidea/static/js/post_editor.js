(function($){

$(function(){
    //xadmin
    //var $content_md = $('#id_content_md');
    //var $content_ck = $('#id_content_ck');
    //admin
    var $content_md = $('div.field-content_md');
    var $content_ck = $('div.field-content_ck');

    var $is_md = $('input[name=is_md]');
    //var $is_md = $('#id_is_md');

    var switch_editor = function(is_md) {
        if (is_md) {
            $content_md.show();
            $content_ck.hide();
        } else {
            $content_md.hide();
            $content_ck.show();
        }
    }
	$is_md.on('click', function() {
    	    switch_editor($(this).is(':checked'));
    	});
	//$('body').on('click','#id_is_md', function() {
	//    console.log(2333)
        //    switch_editor($(this).is(':checked'));
    	//});

    switch_editor($is_md.is(':checked'));
});

})(django.jQuery);
