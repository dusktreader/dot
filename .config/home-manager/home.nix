{ config, pkgs, ... }:

{
  home.username = "dusktreader";
  home.homeDirectory = "/home/dusktreader";

  home.stateVersion = "25.05"; # Read docs before changing.

  targets.genericLinux.enable = true;

  home.packages = [
    pkgs.htop
    pkgs.yq
    pkgs.nerd-fonts.fira-code
    pkgs.ripgrep
  ];

  home.file = {
    ".config/oh-my-posh/config.json".source = "${config.home.homeDirectory}/src/dusktreader/dot/.config/oh-my-posh/config.json";
    # ".config/nvim" = {
    #   source = "${config.home.homeDirectory}/src/dusktreader/dot/.config/nvim";
    #   recursive = true;
    # };

  };

  home.sessionVariables = {
    EDITOR = "nvim";
  };

  programs.zsh = {
    enable = true;
    initContent = ''
      bindkey -e
    '';
  };

  programs.neovim = {
    enable = true;
    viAlias = true;
    vimAlias = true;
    vimdiffAlias = true;
  };

  programs.oh-my-posh = {
    enable = true;
    enableZshIntegration = true;
  };

  # Let Home Manager install and manage itself.
  programs.home-manager = {
    enable = true;
  };
}
