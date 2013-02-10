function updatePreview(edit, preview){
    var content = $('#' + edit).val().replace(/[\n]/g, '<br>');
    $('#' + preview).html(content);
}

function fixText(){
    text = $('#editHome').val().replace(/<br>/g, '\n');
    $('#editHome').html(text);
    text = $('#editSidebar').val().replace(/<br>/g, '\n');
    $('#editSidebar').html(text);
}

$("#editHome").keyup(function(){
    updatePreview("editHome", "homePreview");
});

$('#editSidebar').keyup(function(){
    updatePreview("editSidebar", "sidebarPreview")
});

$('#saveInfo').click(function(){
    var frontPage = $('#editHome').val()
    var sidebar = $('#editSidebar').val()

    var data = {'frontPage': frontPage, 'sidebar': sidebar};
 
    $.ajax({
        type: "POST",
        url: '/editinfo',
        data: data,
        success: function(){
            window.location.href='/';
        }

    })
});

updatePreview('editHome', 'homePreview');
updatePreview('editSidebar', 'sidebarPreview');

fixText();