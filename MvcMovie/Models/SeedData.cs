using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using MvcMovie.Data;

namespace MvcMovie.Models;

public static class SeedData
{
    public static void Initialize(IServiceProvider serviceProvider)
    {
        using var context = new MvcMovieContext(
            serviceProvider.GetRequiredService<DbContextOptions<MvcMovieContext>>());

        if (context.Movie.Any())
        {
            return;
        }

        context.Movie.AddRange(
            new Movie
            {
                Title = "Black Panther",
                ReleaseDate = DateTime.Parse("2018-02-16"),
                Genre = "Action",
                Price = 9.99M,
                Rating = "PG-13"
            },
            new Movie
            {
                Title = "The Lion King",
                ReleaseDate = DateTime.Parse("1994-06-24"),
                Genre = "Animation",
                Price = 7.99M,
                Rating = "G"
            },
            new Movie
            {
                Title = "Inception",
                ReleaseDate = DateTime.Parse("2010-07-16"),
                Genre = "Sci-Fi",
                Price = 8.99M,
                Rating = "PG-13"
            },
            new Movie
            {
                Title = "The Matrix",
                ReleaseDate = DateTime.Parse("1999-03-31"),
                Genre = "Sci-Fi",
                Price = 8.99M,
                Rating = "R"
            },
            new Movie
            {
                Title = "Spider-Man",
                ReleaseDate = DateTime.Parse("2002-05-03"),
                Genre = "Action",
                Price = 7.99M,
                Rating = "PG-13"
            }
        );

        context.SaveChanges();
    }
}
