# Jeopardy Trivia Web App

This is my submission for the Capital One January 2020 Software Engineering Summit. 
Link to deployed website: http://jeopardychallenge.herokuapp.com/

## What it does
My web application allows users to search for Jeopardy questions based on a key word/phrase.
Users can also refine their search by value of the clue, air date (minimum to maximum range),
and how many clues they would like to return. Users also have the option to save clues into a 
table of favorite clues. They can also play a Jeopardy game simulation.

## How I built it
This application was built with Dash, a Python framework for building analytical web applications that
is build on top of Plotly.js, React, and Flask. I also used a postgreSQL database along with
SQLalchemy to store all of the categories and their IDs since the API only allows 100 clues to be
returned at a time. Finally, I used Dash Bootstrap Components for styling. 

## Challenges I ran into
Dash is a really awesome framework, especially for individuals such as myself who don't have a
lot of experience with front end technologies. Dash served its purpose beautifully for
the search engine and saving to favorites. However, since it is also a relatively new framework,
it does have its limitations, and I was held back by a lot of these when trying to implement the Jeopardy game. At the moment, multiple Dash callbacks cannot update the same
output. This resulted in some pretty ugly callbacks (I have one callback that has over 20 inputs and 50 outputs)
which I tried very hard to avoid but unfortunately, but after a lot of experimentation and trying to find
workarounds, was unable to. I also ran into some issues with styling the page because of the way
Dash dynamically generates some of the page elements and so the UI is a little more bland than
I would have liked. The load time of the Jeopardy board also isn't where I would like it to be but that's something
I would love to tackle if I had more time.

## Accomplishments that I'm proud of
I had never used a database before so I was pretty proud of teaching myself the basics of PostgreSQL as well as SQLAlchemy. 
I had also never deployed a website to Heroku before so that was another great learning experience. Although I had used Dash for a previous project,
I think that project would be considered a more typical use case for Dash so on this project, I ended up
having to do a lot of out of the box thinking to get the functionality I needed from Dash. I'm also pretty proud
of being able to implement both of the bonuses.



