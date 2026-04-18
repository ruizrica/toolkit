function getMermaidNormalizationBrowserScript(functionName = "normalizeMermaidSource") {
  return `
function ${functionName}(source) {
  return String(source || '').replace(/([A-Za-z0-9_:-]+)\\[\\/([^\\]\\n]+)\\]/g, function(match, nodeId, label) {
    var trailingWhitespaceMatch = label.match(/\\s*$/);
    var trailingWhitespace = trailingWhitespaceMatch ? trailingWhitespaceMatch[0] : '';
    var coreLabel = trailingWhitespace ? label.slice(0, -trailingWhitespace.length) : label;
    if (coreLabel.endsWith('/')) return match;
    return nodeId + '[/' + coreLabel + '/' + trailingWhitespace + ']';
  });
}
`.trim();
}

module.exports = {
  getMermaidNormalizationBrowserScript,
};
