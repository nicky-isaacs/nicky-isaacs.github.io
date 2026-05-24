require "rake"

CHROME    = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SITE_DIR  = "_site"
PDF_OUT   = "resume.pdf"
PII_FILE  = "_data/pii.yml"
PII_EXAMPLE = "_data/pii.example.yml"

desc "Serve the site locally with live reload"
task :serve do
  sh "bundle exec jekyll serve --livereload"
end

desc "Build the site"
task :build do
  sh "bundle exec jekyll build"
end

desc "Generate a submission-ready PDF resume (requires #{PII_FILE})"
task pdf: :build do
  unless File.exist?(PII_FILE)
    abort "ERROR: #{PII_FILE} not found.\nRun `rake pii:init` and fill in your details first."
  end

  resume_html = File.expand_path("#{SITE_DIR}/resume/index.html")
  unless File.exist?(resume_html)
    abort "ERROR: #{resume_html} not found after build."
  end

  sh %("#{CHROME}" --headless --disable-gpu --no-pdf-header-footer \
       --print-to-pdf="#{File.expand_path(PDF_OUT)}" \
       "file://#{resume_html}")

  puts "\nPDF written to #{PDF_OUT}"
end

namespace :pii do
  desc "Copy #{PII_EXAMPLE} to #{PII_FILE} for first-time setup"
  task :init do
    if File.exist?(PII_FILE)
      puts "#{PII_FILE} already exists — skipping. Edit it directly to update your details."
    else
      cp PII_EXAMPLE, PII_FILE
      puts "Created #{PII_FILE} — open it and fill in your real details."
    end
  end
end

task default: :serve
