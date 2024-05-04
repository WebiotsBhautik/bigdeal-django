const gulp = require("gulp");
const sass = require("gulp-sass");
const autoprefixer = require("gulp-autoprefixer");
const sourcemaps = require("gulp-sourcemaps");
const browserSync = require("browser-sync").create();
const feather = require('feather-icons');

//scss to css
function style() {
    return gulp.src('assets/scss/backend-1.scss', { sourcemaps: true })
        .pipe(sass({
            outputStyle: 'compressed'
        }).on('error', sass.logError))
        .pipe(autoprefixer('last 2 versions'))
        .pipe(gulp.dest('assets/css', { sourcemaps: '.' }))
        .pipe(browserSync.reload({ stream: true }));
}



// Watch function
function watch() {
    browserSync.init({
        proxy: "http://127.0.0.1:8000/admin/",
    });
    gulp.watch("assets/scss/backend-1.scss", style);
    gulp.watch("http://127.0.0.1:8000/admin/").on("change", browserSync.reload);
    gulp.watch("assets/css/backend-1.css").on("change", browserSync.reload);
}

exports.style = style;
exports.watch = watch;

const build = gulp.series(watch);
gulp.task("default", build, "browser-sync");
