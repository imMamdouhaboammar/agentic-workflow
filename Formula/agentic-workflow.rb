class AgenticWorkflow < Formula
  desc "Pluripotent stem-cell framework and universal agentic toolchain for autonomous workflows"
  homepage "https://github.com/imMamdouhaboammar/agentic-workflow"
  url "https://github.com/imMamdouhaboammar/agentic-workflow/archive/refs/tags/v1.2.0.tar.gz"
  license "MIT"

  depends_on "oven-sh/bun/bun" => :recommended
  depends_on "python@3.11" => :recommended

  def install
    libexec.install Dir["*"]
    bin.install_symlink libexec/"bin/cli.js" => "agentic-workflow"
  end

  test do
    assert_match "agentic-workflow v1.2.0", shell_output("#{bin}/agentic-workflow --version")
  end
end
