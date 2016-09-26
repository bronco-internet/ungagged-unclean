$win=$(window)

$(document).ready(function()
	{
	$('#urls').submit(function(e){e.preventDefault();$('#results').html('<p style="text-align:center;margin:25% 0"><img src="/static/loading.gif" alt=""/></p>');$.post('/',$(this).closest('form').serialize(),function(data){$('#results').html(data)})})
	logo_pos()
	$win.resize(function(){logo_pos()})
	})
	
function logo_pos(){$('#logo').css('top',$win.height()-66)}
	
	

	
