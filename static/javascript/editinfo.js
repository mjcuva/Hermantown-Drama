function updatePreview(edit, preview){
    var content = $('#' + edit).val();
    $('#' + preview).html(content);
}

$("#editHome").keyup(function(){
    updatePreview("editHome", "homePreview");
});

$('#editSidebar').keyup(function(){
    updatePreview("editSidebar", "sidebarPreview")
})