var runSequence = require('run-sequence');
var path = require('path');
var fs = require('fs');

var gulp = require('gulp');
var browserify = require('gulp-browserify');
var concat = require('gulp-concat');
var inject = require('gulp-inject');
var dotify = require('gulp-dotify');
var concat = require('gulp-concat');
var header = require('gulp-header');
var uglify = require('gulp-uglify');
var clean = require('gulp-clean');
var less = require('gulp-less');
var imagemin = require('gulp-imagemin');
var rev = require('gulp-rev');
var rev_css_url = require('gulp-rev-css-url');
var htmlmin = require('gulp-htmlmin');
var gzip = require('gulp-gzip');

var pngquant = require('imagemin-pngquant');



var project = {
  paths: {
    output: {
      html: 'baobab/front/templates',
      pyproject: 'baobab',
      static: 'baobab/static'
    },
    input: {
      base: 'baobab.front',
      views: 'views',
      images: 'images',
      assets: 'assets',
      js: 'js/main.js',
      less: 'less/main.less'
    }
  },
  shim: {
  }
}

gulp.task('vendors', function() {
});

gulp.task('assets', function() {
  gulp.src(path.join(project.paths.input.base, 'assets/**/*'))
      .pipe(gulp.dest(path.join(project.paths.output.static, 'assets')));
});

gulp.task('build-templates', function() {
  gulp.src(path.join(project.paths.input.base, project.paths.input.views, '/**/*.html'))
      .pipe(dotify())
      .pipe(concat('templates.js'))
      .pipe(header('module.exports = JST = {};'))
      .pipe(gulp.dest(path.join(project.paths.input.base, 'js')))
});

gulp.task('build-scripts', ['build-templates'], function() {
  if (process.env.TEST == 'TRUE') {
    return gulp.src([path.join(project.paths.input.base, project.paths.input.js)])
        .pipe(browserify({
          shim: project.shim,
          transform: ['aliasify'],
        })).pipe(gulp.dest(path.join(project.paths.output.static, 'js')));
  } else {
    return gulp.src([path.join(project.paths.input.base, project.paths.input.js)])
        .pipe(browserify({
          shim: project.shim
        })).pipe(gulp.dest(path.join(project.paths.output.static, 'js')));
  }
});
gulp.task('build-scripts-vendors', function() {
  return gulp.src([
      'node_modules/html5shiv/dist/html5shiv.js'
    ]).pipe(gulp.dest(path.join(project.paths.output.static, 'js')));
});

gulp.task('build-styles', function() {
  return gulp.src([path.join(project.paths.input.base, project.paths.input.less)])
    .pipe(less())
    .pipe(gulp.dest(project.paths.output.static))
});

gulp.task('build-images', function() {
  return gulp.src([path.join(project.paths.input.base, project.paths.input.images, '**/*.{png,jpg,gif,svg}')])
    .pipe(imagemin({
      optimizationLevel: 7,
      progressive: true,
      svgoPlugins: [{removeViewBox: false}],
      use: [pngquant()]
    }))
    .pipe(gulp.dest(path.join(project.paths.output.static, 'images')))
});

gulp.task('build-html', function() {
  return gulp
    .src(path.join(project.paths.input.base, 'index.html'))
    .pipe(inject(gulp.src(path.join(project.paths.output.static, 'js/html5shiv*.js'), {read: false}), {
      starttag: '<!-- inject:head:{{ext}} -->',
      ignorePath: [project.paths.output.pyproject],
      transform: function(filepath) {
        return '<!--[if lt IE 9]><script src="'+ filepath +'"></script><![endif]-->';
      }
    }))
    .pipe(
      inject(gulp
        .src([
          path.join(project.paths.output.static, 'images/*.ico'),
          path.join(project.paths.output.static, 'js/main*.js'),
          path.join(project.paths.output.static, 'main*.css'),
        ], { read: false }),
        {
          transform: function (filepath) {
            if (filepath.slice(-4) === '.ico') {
              return '<link rel="shortcut icon" href="'+ filepath +'" type="image/x-icon">' +
                     '<link rel="icon" href="'+          filepath +'" type="image/x-icon">';
            }
            // Use the default transform as fallback:
            return inject.transform.apply(inject.transform, arguments);
          },
          ignorePath: [project.paths.output.pyproject],
        }
      )
    )
    .pipe(htmlmin({
      collapseWhitespace: true,
      removeComments: true,
      maxLineLength: 200
    }))
    .pipe(gulp.dest(project.paths.output.html));
});

gulp.task('build', ['assets'], function(callback) {
  runSequence(['build-scripts', 'build-scripts-vendors'], 'build-styles', 'build-images',
              'build-html',
              callback);
});

gulp.task('minify-move', function() {
  fs.mkdirSync(project.paths.output.static+'.tmp');
  fs.mkdirSync(project.paths.output.static+'.tmp/js');
  fs.renameSync(path.join(project.paths.output.static, 'js/main.js'),
                path.join(project.paths.output.static+'.tmp', 'js/main.js'));
});

gulp.task('minify-uglify', function() {
  return gulp.src(path.join(project.paths.output.static+'.tmp', 'js/*.js'))
    .pipe(uglify())
    .pipe(gulp.dest(path.join(project.paths.output.static, 'js')));
});

gulp.task('minify-clean', function() {
  return gulp.src(project.paths.output.static+'.tmp')
      .pipe(clean());
});

gulp.task('minify', function(callback) {
  runSequence('minify-move',
              'minify-uglify',
              'minify-clean',
              callback);

});

gulp.task('rev-move', function() {
  fs.mkdirSync(project.paths.output.static+'.tmp');
  fs.renameSync(path.join(project.paths.output.static, 'main.css'),
                path.join(project.paths.output.static+'.tmp', 'main.css'));
  fs.renameSync(path.join(project.paths.output.static, 'images'),
                path.join(project.paths.output.static+'.tmp', 'images'));
  fs.renameSync(path.join(project.paths.output.static, 'js'),
                path.join(project.paths.output.static+'.tmp', 'js'));
});

gulp.task('rev-inject', function() {
  return gulp.src(project.paths.output.static+'.tmp/**/*')
    .pipe(rev())
    .pipe(rev_css_url())
    .pipe(gulp.dest(project.paths.output.static))
    .pipe(rev.manifest())
    .pipe(gulp.dest(project.paths.output.static));
});

gulp.task('rev-clean', function() {
  return gulp.src(project.paths.output.static+'.tmp')
      .pipe(clean());
});

gulp.task('rev', function(callback) {
  runSequence('rev-move',
              'rev-inject',
              'rev-clean',
              'build-html',
              callback);
});

gulp.task('gzip', function() {
  return gulp.src(project.paths.output.static+'/**/*')
    .pipe(gzip({ gzipOptions: { level: 9 } }))
    .pipe(gulp.dest(project.paths.output.static))
});


gulp.task('dev', ['build'], function() {
  return gulp.watch([
      path.join(project.paths.input.base, '**/*.html'),
      path.join(project.paths.input.base, '**/*.js'),
      path.join(project.paths.input.base, '**/*.less')
    ], ['build']);
});

gulp.task('test-protractor', function() {
  var protractor = require("gulp-protractor").protractor;
  return gulp.src(["baobab.front/tests/integration/*.js"])
    .pipe(protractor({
        configFile: "protractor.conf.js",
        args: ['--baseUrl', 'http://127.0.0.1:8000']
    })) 
    .on('error', function(e) { throw e })
});

gulp.task('test', function(callback) {
  process.env.TEST = 'TRUE';

  runSequence('vendors',
              'build',
              'test-protractor',
              callback);
});

gulp.task('release', function(callback) {
  runSequence('vendors',
              'build',
              'minify',
              'rev',
              'gzip',
              callback);
});


