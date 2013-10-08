window.app = {
  init: function() {
    this.lookup();
    $('.refresh').click(function() {
      window.app.lookup();
    });
  },

  display: function(data) {
    $('.loading').addClass('hidden');
    window.app.displayScore(data.score);
    window.app.displayRecent(data.recent);
  },

  displayScore: function(score) {
    $('h2.score').text(Math.round(score.combined));
    $('h2.violent-score').text(Math.round(score.violent));
    $('h2.nonviolent-score').text(Math.round(score.nonviolent));
    $('.score-container').removeClass('hidden');
  },

  displayRecent: function(recent) {
    $('.recent-container table tbody').empty();
    $.each(recent, function(index, record) {
      tr = $("<tr>");
      tr.append($("<td>" + record.dispatch_time.split('T')[0] + "</td>"));
      tr.append($("<td>" + record.location + "</td>"));
      tr.append($("<td>" + record.description + "</td>"));
      tr.append($("<td>" + Math.round(record.distance) + "</td>"));
      $('.recent-container table tbody').append(tr);
    });
    $('.recent-container').removeClass('hidden');
  },

  lookup: function() {
    $('.loading').removeClass('hidden');
    $('.score-container').addClass('hidden');
    $('.recent-container').addClass('hidden');

    if (!navigator.geolocation) {
      alert('Location is disabled on your device');
      return;
    }

    navigator.geolocation.getCurrentPosition(app.updatePosition);
  },

  updatePosition: function(position) {
    var promise = $.get('/api/', 
      {lon: position.coords.longitude, lat: position.coords.latitude});

    promise.done(function(data) {
      window.app.display(data);
    });

    promise.fail(function() {
      alert("Couldn't load information for your location");
    });
  },
};
