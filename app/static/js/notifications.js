// checks for notifications
function set_task_progress(task_id, progress) {
    $('#' + task_id + '-progress').text(progress);
  }
  
var changeDiv = false;

  $(function() {
    var since = 0;
    setInterval(function() {
        $.getJSON('/notifications', {since: since},
            function(notifications) {
              if (changeDiv == 'No results') {
                $('#notif').html(
                  `
                <div class="alert alert-danger" role="alert">
                   <span id="{{ task.id }}-progress">` + changeDiv + `</span>
                </div>
                `
                );
              }
              else if (changeDiv == "Export complete") {
                $('#notif').html(
                  `
                <div class="alert alert-success" role="alert">
                   <span id="{{ task.id }}-progress">` + changeDiv + `</span>
                </div>
                `
                );
              }
              for (var i = 0; i < notifications.length; i++) {
                switch (notifications[i].name) {
                    case 'task_progress':
                        set_task_progress(
                            notifications[i].data.task_id,
                            notifications[i].data.progress);
                            if (notifications[i].data.progress == 100) {
                              changeDiv = notifications[i].data.result;
                            };
                        break;
                }
                since = notifications[i].timestamp;
              }
            }
        );
    }, 2500);
  });


