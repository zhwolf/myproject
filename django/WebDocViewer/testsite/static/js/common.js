function deleteConfirm() {
    if (!confirm( arguments.length == 0 ? "确认要删除该数据？" : arguments[0]  )) 
    {
            window.event.returnValue = false;
    }
}

function collectfavorite(url)
{
        $.ajax({      
            cache:false,
            type: "GET",      
            url: url,      
            dataType:   "json",      
            success: function(json){      
                alert(json.msg);
            }       
        })         
}  