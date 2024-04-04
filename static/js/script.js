$(document).ready(function () {
    $('#commentForm').submit(function (event) {
        event.preventDefault();
        var formData = $(this).serialize();
        $('#loadingMessage').show();
        $.ajax({
            type: 'POST',
            url: '/sentiment_analysis',
            data: formData,
            success: function (response) {
                $('#loadingMessage').hide();
                // Process JSON response and update the results and charts
                $('#results').html('<h2 class="mb-4">Results</h2>');

                // Update basic sentiment analysis data
                // $('#results').append('<div class="row"><h3>Video ID: ' + response.video_id + '</h3></div>');
                $('#results').append('<div class="row"><h3>Positive Count: ' + response.positive_count + '</h3></div>');
                $('#results').append('<div class="row"><h3>Negative Count: ' + response.negative_count + '</h3></div>');
                $('#results').append('<div class="row"><h3>Neutral Count: ' + response.neutral_count + '</h3></div>');
                // $('#results').append('<div class="row"><h3>Overall Sentiment Score: ' + response.overall_sentiment_score + '</h3></div>');

                // Update suggestion comments
                $('#results').append('<div class="row1"><h3>Suggestion Comments:</h3></div>');
                response.suggestion_comments.forEach(function(comment) {
                    $('.row1').append('<p>' + comment + '</p>');
                });

                // Update most frequent words
                $('#results').append('<div class="row2"><h3>Most Frequent Words in Comments:</h3></div>');
                response.frequent_words.forEach(function(word) {
                    $('.row2').append('<p>' + word[0] + ': ' + word[1] + ' times</p>');
                });

                // Update sentiment analysis pie chart
                var positiveCount = response.positive_count;
                var negativeCount = response.negative_count;
                var neutralCount = response.neutral_count;

                var positiveData = {
                    values: [positiveCount, negativeCount, neutralCount],
                    labels: ['Positive', 'Negative', 'Neutral'],
                    type: 'pie',
                    marker: {
                        colors: ['#36C75A', '#FF6F61', '#6E6E6E']
                    }
                };
                
                var layoutPositive = {
                    title: 'Sentiment Analysis Pie Chart',
                    legend: {
                        orientation: 'h',
                        y: 0.95
                    }
                };
                
                Plotly.newPlot('positiveChart', [positiveData], layoutPositive);

                // Update sentiment analysis bar chart
                var barData = [{
                    x: ['Positive', 'Negative', 'Neutral'],
                    y: [positiveCount, negativeCount, neutralCount],
                    type: 'bar'
                }];

                var layout = {
                    title: 'Sentiment Analysis Bar Chart',
                    xaxis: { title: 'Sentiment' },
                    yaxis: { title: 'Count' }
                };

                Plotly.newPlot('barChart', barData, layout);
            },
            error: function (xhr, status, error) {
                console.error(xhr.responseText);
                $('#loadingMessage').hide();
            }
        });
        return false; // Prevents the page from scrolling to the top
    });
});