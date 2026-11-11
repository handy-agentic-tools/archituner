LINE = "/" + "/"


SCRIPT = (r"""const DATA = __DATA__;
const $ = s => document.querySelector(s);
const views = ["layers", "matrix", "coverage"];
""" + LINE +
          r""" Decision 18: the layers diagram opens - an architecture overview is the
""" + LINE +
          r""" picture a person means by the word. The matrix is one switch away.
let current = "layers";
let selection = null;   """ + LINE +
          r""" {kind: "pair"|"layer"|"file", id}
const pairAt = {};
DATA.pairs.forEach(p => pairAt[p.source + "->" + p.target] = p);

""" + LINE +
          r""" Anything the reading carries as prose - a contract line, a finding, a remedy -
""" + LINE +
          r""" reaches the page as text and never as markup, so one escape and one place it
""" + LINE +
          r""" is spelled. One function, for text and attributes alike: the page writes its
""" + LINE +
          r""" attributes in single quotes and a measured name may hold an apostrophe, a
""" + LINE +
          r""" quote or an angle bracket, so every value a measurement names goes through it
""" + LINE +
          r""" and no raw concatenation of a name reaches the page.
const esc = t => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;")
  .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");

""" + LINE +
          r""" --- the two readings --------------------------------------------------------
""" + LINE +
          r""" Decision 8: two runs are one map of differences, never two maps. There is one
""" + LINE +
          r""" set of views; `reading` says which of the two readings they are drawn in, and
""" + LINE +
          r""" they are never both on screen, because a mark saying what a pair is and what
""" + LINE +
          r""" it did has two answers and the reader takes one for the other.
const CHANGE = DATA.change || null;
const OUTCOMES = ["improved", "unchanged", "regressed"];
""" + LINE +
          r""" `dropped` is not a fourth outcome. It is the pair the baseline and this run do
""" + LINE +
          r""" not both name, which the spec says to state as dropped rather than report as
""" + LINE +
          r""" moved - so it is a mark and a count, and never one of the three.
const MOVES = OUTCOMES.concat(["dropped"]);
""" + LINE +
          r""" Marks the state reading does not use, so which reading is on screen is never
""" + LINE +
          r""" in doubt, and each survives greyscale on its own shape.
const MOVED = __MOVED_MAP__;
let reading = "state";
const changing = () => reading === "change" && !!CHANGE;

function moveOf(source, target) {
  return (CHANGE && CHANGE.pairs[source + " -> " + target]) || "dropped";
}

function layerMove(name) {
  """ + LINE +
          r""" A layer carries what its own pairs did. A regression outranks an
  """ + LINE +
          r""" improvement: a layer that gained one permitted edge and realised one
  """ + LINE +
          r""" forbidden edge has got worse, and the reader is here for the worse one.
  let seen = null;
  for (const key in CHANGE.pairs) {
    const ends = key.split(" -> ");
    if (ends[0] !== name && ends[1] !== name) continue;
    const move = CHANGE.pairs[key];
    if (move === "regressed") return "regressed";
    if (move === "improved") seen = "improved";
    else if (!seen) seen = "unchanged";
  }
  return seen || "dropped";   """ + LINE +
          r""" a layer the baseline never named
}

const LAYER_MOVE = {};
if (CHANGE) DATA.order.forEach(n => LAYER_MOVE[n] = layerMove(n));
""" + LINE +
          r""" Step 14: measured, not inherited. What a file did is in the two file tables,
""" + LINE +
          r""" so nothing here asks what the file's layer's pairs did.
const fileMove = f => (CHANGE && CHANGE.files[f.path]) || "dropped";
const RANK = {regressed: 3, improved: 2, unchanged: 1, dropped: 0};
""" + LINE +
          r""" A region is many files, and one regression is what the reader came for, so the
""" + LINE +
          r""" worst outcome any member carries is the one the box shows.
const regionMove = members => members.reduce((worst, path) => {
  const move = fileMove({path: path});
  return RANK[move] > RANK[worst] ? move : worst;
}, "dropped");
const relocation = path => CHANGE && CHANGE.relocations[path];

function drawTree() {
  """ + LINE +
          r""" uispec region 2: the tree's name, then the verdict. A reader who did not run
  """ + LINE +
          r""" the tool has nothing else on the page saying which project this is - the
  """ + LINE +
          r""" contract's own filename cannot, since every tree calls it the same thing.
  """ + LINE +
          r""" The name and no label: uispec gives it none. The name and never the path,
  """ + LINE +
          r""" because a rendered page travels and a path stops meaning anything when it
  """ + LINE +
          r""" does; the run hands over a directory's name, not a directory.
  $("#tree").textContent = DATA.tree;
}

function verdict() {
  """ + LINE +
          r""" Decision 3: the conformance answer stands here at a cold open and costs
  """ + LINE +
          r""" nothing to read. It is all this region carries now. Walk row 2 took the
  """ + LINE +
          r""" counts row away - three controls carried the state axis, this row and the
  """ + LINE +
          r""" legend each carrying the counts as well, so a reader met one state three
  """ + LINE +
          r""" times and isolating it in one of the three left the other two saying
  """ + LINE +
          r""" something else. The legend is the one that kept the counts, because a
  """ + LINE +
          r""" legend entry is already the control that reaches their members.
  const c = DATA.counts;
  const bad = c.divergence > 0;
  $("#verdict").className = bad ? "bad" : "good";
  $("#verdict").innerHTML = "<h1>" + (bad
    ? "DIVERGENT: " + c.divergence + " forbidden pair(s) realised"
    : "CONFORMS: no forbidden pair realised") + "</h1>";
}

function drawReading() {
  """ + LINE +
          r""" The toggle. With no baseline stored it still says so and still names the
  """ + LINE +
          r""" command that writes one, because an empty diff would read as "nothing
  """ + LINE +
          r""" moved", which is the one thing it does not mean. The line naming what a
  """ + LINE +
          r""" change is measured against, and the count of pairs dropped from it, left
  """ + LINE +
          r""" with the other large labels and are the Help's to carry now.
  """ + LINE +
          r""" The contract's name, run from its own directory: the page carries no path,
  """ + LINE +
          r""" because a rendered page travels and a path stops meaning anything when it does.
  const command = "python3 -m archituner " + DATA.contract + " --baseline";
  const off = r => r === "change" && !CHANGE;
  $("#reading").innerHTML = ["state", "change"].map(r =>
    "<button class='" + (r === reading ? "on" : "") + "' data-reading='" + esc(r) + "'"
    + (off(r) ? " aria-disabled='true' title='no baseline is stored for this contract, "
       + "so there is nothing to compare this run against. Write one with " + esc(command)
       + " from the directory that holds the contract, then render again.'" : "")
    + ">" + esc(r) + " reading"
    + (off(r) ? " · no baseline stored" : "") + "</button>").join("");
}

""")
