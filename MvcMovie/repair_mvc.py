from pathlib import Path

LT = chr(60)
GT = chr(62)
ARROW = "=>"

def write(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = content.replace("[[LT]]", LT).replace("[[GT]]", GT).replace("[[ARROW]]", ARROW)
    p.write_text(content, encoding="utf-8")

write("Program.cs", r'''
using Microsoft.EntityFrameworkCore;
using MvcMovie.Data;
using MvcMovie.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();

builder.Services.AddDbContext<MvcMovieContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("MvcMovieContext")));

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var services = scope.ServiceProvider;
    SeedData.Initialize(services);
}

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Movies}/{action=Index}/{id?}");

app.Run();
'''.strip() + "\n")

write("Models/Movie.cs", r'''
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MvcMovie.Models;

public class Movie
{
    public int Id { get; set; }

    [StringLength(60, MinimumLength = 3)]
    [Required]
    public string? Title { get; set; }

    [Display(Name = "Release Date")]
    [DataType(DataType.Date)]
    public DateTime ReleaseDate { get; set; }

    [RegularExpression(@"^[A-Z]+[a-zA-Z\s-]*$")]
    [Required]
    [StringLength(30)]
    public string? Genre { get; set; }

    [Range(1, 100)]
    [DataType(DataType.Currency)]
    [Column(TypeName = "decimal(18, 2)")]
    public decimal Price { get; set; }

    [RegularExpression(@"^[A-Z]+[a-zA-Z0-9""'\s-]*$")]
    [StringLength(5)]
    [Required]
    public string? Rating { get; set; }
}
'''.strip() + "\n")

write("Models/MovieGenreViewModel.cs", r'''
using Microsoft.AspNetCore.Mvc.Rendering;

namespace MvcMovie.Models;

public class MovieGenreViewModel
{
    public List<Movie>? Movies { get; set; }
    public SelectList? Genres { get; set; }
    public string? MovieGenre { get; set; }
    public string? SearchString { get; set; }
    public int? SearchYear { get; set; }
}
'''.strip() + "\n")

write("Data/MvcMovieContext.cs", r'''
using Microsoft.EntityFrameworkCore;
using MvcMovie.Models;

namespace MvcMovie.Data;

public class MvcMovieContext : DbContext
{
    public MvcMovieContext(DbContextOptions<MvcMovieContext> options)
        : base(options)
    {
    }

    public DbSet<Movie> Movie { get; set; } = default!;
}
'''.strip() + "\n")

write("Models/SeedData.cs", r'''
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
'''.strip() + "\n")

write("Controllers/MoviesController.cs", r'''
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using MvcMovie.Data;
using MvcMovie.Models;

namespace MvcMovie.Controllers;

public class MoviesController : Controller
{
    private readonly MvcMovieContext _context;

    public MoviesController(MvcMovieContext context)
    {
        _context = context;
    }

    public async Task<IActionResult> Index(string movieGenre, string searchString, int? searchYear)
    {
        IQueryable<string> genreQuery = from m in _context.Movie
                                        orderby m.Genre
                                        select m.Genre;

        var movies = from m in _context.Movie
                     select m;

        if (!string.IsNullOrEmpty(searchString))
        {
            movies = movies.Where(s => s.Title!.ToUpper().Contains(searchString.ToUpper()));
        }

        if (!string.IsNullOrEmpty(movieGenre))
        {
            movies = movies.Where(x => x.Genre == movieGenre);
        }

        if (searchYear.HasValue)
        {
            movies = movies.Where(x => x.ReleaseDate.Year >= searchYear.Value);
        }

        var movieGenreVM = new MovieGenreViewModel
        {
            Genres = new SelectList(await genreQuery.Distinct().ToListAsync()),
            Movies = await movies.ToListAsync(),
            MovieGenre = movieGenre,
            SearchString = searchString,
            SearchYear = searchYear
        };

        return View(movieGenreVM);
    }

    public async Task<IActionResult> Details(int? id)
    {
        if (id == null)
        {
            return NotFound();
        }

        var movie = await _context.Movie.FirstOrDefaultAsync(m => m.Id == id);

        if (movie == null)
        {
            return NotFound();
        }

        return View(movie);
    }

    public IActionResult Create()
    {
        return View();
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Create([Bind("Id,Title,ReleaseDate,Genre,Price,Rating")] Movie movie)
    {
        if (ModelState.IsValid)
        {
            _context.Add(movie);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Index));
        }

        return View(movie);
    }

    public async Task<IActionResult> Edit(int? id)
    {
        if (id == null)
        {
            return NotFound();
        }

        var movie = await _context.Movie.FindAsync(id);

        if (movie == null)
        {
            return NotFound();
        }

        return View(movie);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Edit(int id, [Bind("Id,Title,ReleaseDate,Genre,Price,Rating")] Movie movie)
    {
        if (id != movie.Id)
        {
            return NotFound();
        }

        if (ModelState.IsValid)
        {
            _context.Update(movie);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Index));
        }

        return View(movie);
    }

    public async Task<IActionResult> Delete(int? id)
    {
        if (id == null)
        {
            return NotFound();
        }

        var movie = await _context.Movie.FirstOrDefaultAsync(m => m.Id == id);

        if (movie == null)
        {
            return NotFound();
        }

        return View(movie);
    }

    [HttpPost, ActionName("Delete")]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DeleteConfirmed(int id)
    {
        var movie = await _context.Movie.FindAsync(id);

        if (movie != null)
        {
            _context.Movie.Remove(movie);
        }

        await _context.SaveChangesAsync();
        return RedirectToAction(nameof(Index));
    }
}
'''.strip() + "\n")

write("Views/Movies/Index.cshtml", r'''
@model MvcMovie.Models.MovieGenreViewModel

@{
    ViewData["Title"] = "My Favorite Movies";
}

[[LT]]h1[[GT]]My Favorite Movies[[LT]]/h1[[GT]]

[[LT]]p[[GT]]
    [[LT]]a asp-action="Create"[[GT]]Create New[[LT]]/a[[GT]]
[[LT]]/p[[GT]]

[[LT]]form asp-controller="Movies" asp-action="Index" method="get" class="movie-search-form"[[GT]]
    [[LT]]p[[GT]]
        [[LT]]select asp-for="MovieGenre" asp-items="Model.Genres"[[GT]]
            [[LT]]option value=""[[GT]]All[[LT]]/option[[GT]]
        [[LT]]/select[[GT]]

        [[LT]]label asp-for="SearchString"[[GT]]Title:[[LT]]/label[[GT]]
        [[LT]]input type="text" asp-for="SearchString" /[[GT]]

        [[LT]]label asp-for="SearchYear"[[GT]]Year or newer:[[LT]]/label[[GT]]
        [[LT]]input type="number" asp-for="SearchYear" min="1900" max="2100" /[[GT]]

        [[LT]]input type="submit" value="Filter" /[[GT]]
    [[LT]]/p[[GT]]
[[LT]]/form[[GT]]

[[LT]]table class="table"[[GT]]
    [[LT]]thead[[GT]]
        [[LT]]tr[[GT]]
            [[LT]]th[[GT]]Title[[LT]]/th[[GT]]
            [[LT]]th[[GT]]Release Date[[LT]]/th[[GT]]
            [[LT]]th[[GT]]Genre[[LT]]/th[[GT]]
            [[LT]]th[[GT]]Price[[LT]]/th[[GT]]
            [[LT]]th[[GT]]Rating[[LT]]/th[[GT]]
            [[LT]]th[[GT]][[LT]]/th[[GT]]
        [[LT]]/tr[[GT]]
    [[LT]]/thead[[GT]]
    [[LT]]tbody[[GT]]
@foreach (var item in Model.Movies!)
{
        [[LT]]tr[[GT]]
            [[LT]]td[[GT]]@Html.DisplayFor(modelItem [[ARROW]] item.Title)[[LT]]/td[[GT]]
            [[LT]]td[[GT]]@Html.DisplayFor(modelItem [[ARROW]] item.ReleaseDate)[[LT]]/td[[GT]]
            [[LT]]td[[GT]]@Html.DisplayFor(modelItem [[ARROW]] item.Genre)[[LT]]/td[[GT]]
            [[LT]]td[[GT]]@Html.DisplayFor(modelItem [[ARROW]] item.Price)[[LT]]/td[[GT]]
            [[LT]]td[[GT]]@Html.DisplayFor(modelItem [[ARROW]] item.Rating)[[LT]]/td[[GT]]
            [[LT]]td[[GT]]
                [[LT]]a asp-action="Edit" asp-route-id="@item.Id"[[GT]]Edit[[LT]]/a[[GT]] |
                [[LT]]a asp-action="Details" asp-route-id="@item.Id"[[GT]]Details[[LT]]/a[[GT]] |
                [[LT]]a asp-action="Delete" asp-route-id="@item.Id"[[GT]]Delete[[LT]]/a[[GT]]
            [[LT]]/td[[GT]]
        [[LT]]/tr[[GT]]
}
    [[LT]]/tbody[[GT]]
[[LT]]/table[[GT]]
'''.strip() + "\n")

form_view = r'''
@model MvcMovie.Models.Movie

@{
    ViewData["Title"] = "__TITLE__";
}

[[LT]]h1[[GT]]__HEADING__[[LT]]/h1[[GT]]

[[LT]]h4[[GT]]Movie[[LT]]/h4[[GT]]
[[LT]]hr /[[GT]]

[[LT]]div class="row"[[GT]]
    [[LT]]div class="col-md-4"[[GT]]
        [[LT]]form asp-action="__ACTION__" method="post"[[GT]]
            [[LT]]div asp-validation-summary="ModelOnly" class="text-danger"[[GT]][[LT]]/div[[GT]]

            __HIDDEN_ID__

            [[LT]]div class="form-group"[[GT]]
                [[LT]]label asp-for="Title" class="control-label"[[GT]][[LT]]/label[[GT]]
                [[LT]]input asp-for="Title" class="form-control" /[[GT]]
                [[LT]]span asp-validation-for="Title" class="text-danger"[[GT]][[LT]]/span[[GT]]
            [[LT]]/div[[GT]]

            [[LT]]div class="form-group"[[GT]]
                [[LT]]label asp-for="ReleaseDate" class="control-label"[[GT]][[LT]]/label[[GT]]
                [[LT]]input asp-for="ReleaseDate" class="form-control" /[[GT]]
                [[LT]]span asp-validation-for="ReleaseDate" class="text-danger"[[GT]][[LT]]/span[[GT]]
            [[LT]]/div[[GT]]

            [[LT]]div class="form-group"[[GT]]
                [[LT]]label asp-for="Genre" class="control-label"[[GT]][[LT]]/label[[GT]]
                [[LT]]input asp-for="Genre" class="form-control" /[[GT]]
                [[LT]]span asp-validation-for="Genre" class="text-danger"[[GT]][[LT]]/span[[GT]]
            [[LT]]/div[[GT]]

            [[LT]]div class="form-group"[[GT]]
                [[LT]]label asp-for="Price" class="control-label"[[GT]][[LT]]/label[[GT]]
                [[LT]]input asp-for="Price" class="form-control" /[[GT]]
                [[LT]]span asp-validation-for="Price" class="text-danger"[[GT]][[LT]]/span[[GT]]
            [[LT]]/div[[GT]]

            [[LT]]div class="form-group"[[GT]]
                [[LT]]label asp-for="Rating" class="control-label"[[GT]][[LT]]/label[[GT]]
                [[LT]]input asp-for="Rating" class="form-control" /[[GT]]
                [[LT]]span asp-validation-for="Rating" class="text-danger"[[GT]][[LT]]/span[[GT]]
            [[LT]]/div[[GT]]

            [[LT]]div class="form-group mt-2"[[GT]]
                [[LT]]input type="submit" value="__BUTTON__" class="btn btn-primary" /[[GT]]
            [[LT]]/div[[GT]]
        [[LT]]/form[[GT]]
    [[LT]]/div[[GT]]
[[LT]]/div[[GT]]

[[LT]]div class="mt-2"[[GT]]
    [[LT]]a asp-action="Index"[[GT]]Back to List[[LT]]/a[[GT]]
[[LT]]/div[[GT]]

@section Scripts {
    @{await Html.RenderPartialAsync("_ValidationScriptsPartial");}
}
'''.strip() + "\n"

write("Views/Movies/Create.cshtml", form_view.replace("__TITLE__", "Create").replace("__HEADING__", "Create Movie").replace("__ACTION__", "Create").replace("__BUTTON__", "Create").replace("__HIDDEN_ID__", ""))
write("Views/Movies/Edit.cshtml", form_view.replace("__TITLE__", "Edit").replace("__HEADING__", "Edit Movie").replace("__ACTION__", "Edit").replace("__BUTTON__", "Save").replace("__HIDDEN_ID__", '[[LT]]input type="hidden" asp-for="Id" /[[GT]]'))

write("Views/Movies/Details.cshtml", r'''
@model MvcMovie.Models.Movie

@{
    ViewData["Title"] = "Details";
}

[[LT]]h1[[GT]]Movie Details[[LT]]/h1[[GT]]

[[LT]]div[[GT]]
    [[LT]]h4[[GT]]Movie[[LT]]/h4[[GT]]
    [[LT]]hr /[[GT]]

    [[LT]]dl class="row"[[GT]]
        [[LT]]dt class="col-sm-2"[[GT]]Title[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.Title)[[LT]]/dd[[GT]]

        [[LT]]dt class="col-sm-2"[[GT]]Release Date[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.ReleaseDate)[[LT]]/dd[[GT]]

        [[LT]]dt class="col-sm-2"[[GT]]Genre[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.Genre)[[LT]]/dd[[GT]]

        [[LT]]dt class="col-sm-2"[[GT]]Price[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.Price)[[LT]]/dd[[GT]]

        [[LT]]dt class="col-sm-2"[[GT]]Rating[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.Rating)[[LT]]/dd[[GT]]
    [[LT]]/dl[[GT]]
[[LT]]/div[[GT]]

[[LT]]div[[GT]]
    [[LT]]a asp-action="Edit" asp-route-id="@Model?.Id"[[GT]]Edit[[LT]]/a[[GT]] |
    [[LT]]a asp-action="Index"[[GT]]Back to List[[LT]]/a[[GT]]
[[LT]]/div[[GT]]
'''.strip() + "\n")

write("Views/Movies/Delete.cshtml", r'''
@model MvcMovie.Models.Movie

@{
    ViewData["Title"] = "Delete";
}

[[LT]]h1[[GT]]Delete Movie[[LT]]/h1[[GT]]

[[LT]]h3[[GT]]Are you sure you want to delete this movie?[[LT]]/h3[[GT]]

[[LT]]div[[GT]]
    [[LT]]h4[[GT]]Movie[[LT]]/h4[[GT]]
    [[LT]]hr /[[GT]]

    [[LT]]dl class="row"[[GT]]
        [[LT]]dt class="col-sm-2"[[GT]]Title[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.Title)[[LT]]/dd[[GT]]

        [[LT]]dt class="col-sm-2"[[GT]]Release Date[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.ReleaseDate)[[LT]]/dd[[GT]]

        [[LT]]dt class="col-sm-2"[[GT]]Genre[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.Genre)[[LT]]/dd[[GT]]

        [[LT]]dt class="col-sm-2"[[GT]]Price[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.Price)[[LT]]/dd[[GT]]

        [[LT]]dt class="col-sm-2"[[GT]]Rating[[LT]]/dt[[GT]]
        [[LT]]dd class="col-sm-10"[[GT]]@Html.DisplayFor(model [[ARROW]] model.Rating)[[LT]]/dd[[GT]]
    [[LT]]/dl[[GT]]

    [[LT]]form asp-action="Delete" method="post"[[GT]]
        [[LT]]input type="hidden" asp-for="Id" /[[GT]]
        [[LT]]input type="submit" value="Delete" class="btn btn-danger" /[[GT]] |
        [[LT]]a asp-action="Index"[[GT]]Back to List[[LT]]/a[[GT]]
    [[LT]]/form[[GT]]
[[LT]]/div[[GT]]
'''.strip() + "\n")

write("Views/Shared/_Layout.cshtml", r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>@ViewData["Title"] - Edwin Movies</title>
    <link rel="stylesheet" href="~/lib/bootstrap/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="~/css/site.css" asp-append-version="true" />
    <link rel="stylesheet" href="~/MvcMovie.styles.css" asp-append-version="true" />
</head>
<body>
    <header>
        <nav class="navbar navbar-expand-sm navbar-toggleable-sm navbar-light bg-white border-bottom box-shadow mb-3">
            <div class="container-fluid">
                <a class="navbar-brand" asp-area="" asp-controller="Movies" asp-action="Indexr text-muted">
        <div class="container">
            &copy; 2026 - Edwin Movies
        </div>
    </footer>

    <script src="~/lib/jquery/dist/jquery.min.js"></script>
    <script src="~/lib/bootstrap/dist/js/bootstrap.bundle.min.js"></script>
    <script src="~/js/site.js" asp-append-version="true"></script>

    @await RenderSectionAsync("Scripts", required: false)
</body>
</html>
'''.strip() + "\n")

write("appsettings.json", r'''
{
  "ConnectionStrings": {
    "MvcMovieContext": "Data Source=MvcMovie.db"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}
'''.strip() + "\n")

readme = """# CSE 325 W02 Assignment: ASP.NET Core UI MVC

## Student

Edwin Kambale

## Assignment Summary

This repository contains my completed Week 02 ASP.NET Core MVC application based on the Microsoft ASP.NET Core MVC tutorial.

## Required Additional Functionality

- Changed the application title to include my name: Edwin Movies.
- Added at least three of my own movies:
  - Black Panther
  - The Lion King
  - Inception
- Changed the movie listing page heading from Index to My Favorite Movies.
- Added search by year so users can filter movies released in that year or newer.
- Improved form styling by adding padding to input, select, and textarea elements.

## How to Run

Run these commands:

    dotnet restore
    dotnet build
    dotnet run

Then open the localhost URL shown in the terminal.

## Test Search by Year

On the Movies page, enter a year such as 2010 in the year filter. The app displays movies released in 2010 or newer.
"""
Path("README.md").write_text(readme, encoding="utf-8")

css_path = Path("wwwroot/css/site.css")
css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
css = css.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;lt;", "<").replace("&amp;gt;", ">")
if "W02 required styling" not in css:
    css += """

/* W02 required styling: add padding to form input elements */
input,
select,
textarea {
    padding: 8px 10px;
    margin: 4px;
    border-radius: 4px;
}

.movie-search-form {
    margin-bottom: 20px;
}

.movie-search-form label {
    margin-left: 8px;
    font-weight: 600;
}
"""
css_path.write_text(css, encoding="utf-8")
