
{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.selenium
    pkgs.python310Packages.pillow
    pkgs.python310Packages.pytesseract
    pkgs.python310Packages.pandas
    pkgs.tesseract
    pkgs.chromium
  ];
}
