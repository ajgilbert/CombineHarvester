import CombineHarvester.CombineTools.plotting as plot 
import ROOT
import math
import argparse
from array import array

ROOT.gROOT.SetBatch(ROOT.kTRUE)
parser = argparse.ArgumentParser()
parser.add_argument('--files', '-f', help='named input files')
parser.add_argument(
    '--output', '-o', default='limit', help="""Name of the output
    plot without file extension""")
parser.add_argument(
    '--cms-sub', default='Internal', help="""Text below the CMS logo""")
parser.add_argument(
    '--title-right', default='', help="""Right header text above the frame""")
parser.add_argument(
    '--title-left', default='', help="""Left header text above the frame""")
parser.add_argument(
    '--x-title', default='#sigma#font[42]{(gg#phi)}#upoint#font[52]{B}#font[42]{(#phi#rightarrow#tau#tau)} (pb)', help="""Title for the x-axis""")
parser.add_argument(
    '--y-title', default='#sigma#font[42]{(bb#phi)}#upoint#font[52]{B}#font[42]{(#phi#rightarrow#tau#tau)} (pb)', help="""Title for the x-axis""")
parser.add_argument(
    '--debug-output', '-d', help="""If specified, write the contour TH2s and
    TGraphs into this output ROOT file""")
args = parser.parse_args()

#Create canvas and TH2D for each component
plot.ModTDRStyle(width=600, l=0.12)
ROOT.gStyle.SetNdivisions(510, 'XYZ')
plot.SetBirdPalette()
canv = ROOT.TCanvas(args.output, args.output)
pads = plot.OnePad()

if args.debug_output is not None:
    debug = ROOT.TFile(args.debug_output, 'RECREATE')
else:
    debug = None

limit = plot.MakeTChain([args.files], 'limit')
graph = plot.TGraph2DFromTree(
    limit, "r_ggH", "r_bbH", '2*deltaNLL', 'quantileExpected > -0.5 && deltaNLL > 0 && deltaNLL < 1000')
best = plot.TGraphFromTree(
    limit, "r_ggH", "r_bbH", 'quantileExpected > -0.5 && deltaNLL == 0')
plot.RemoveGraphXDuplicates(best)
hists = plot.TH2FromTGraph2D(graph, method='BinCenterAligned')
plot.fastFillTH2(hists, graph,interpolateMissing=True)
hists.SetMaximum(6)
hists.SetMinimum(0)
hists.SetContour(255)
# c2=ROOT.TCanvas()
# hists.Draw("COLZ")
# c2.SaveAs("heatmap.png")
axis =  hists.Clone()
axis.Reset()
axis.GetXaxis().SetTitle(args.x_title)
axis.GetYaxis().SetTitle(args.y_title)

cont_1sigma = plot.contourFromTH2(hists, ROOT.Math.chisquared_quantile_c(1 - 0.68, 2), 10, 20)
cont_2sigma = plot.contourFromTH2(hists, ROOT.Math.chisquared_quantile_c(1 - 0.95, 2), 10, 20)

if debug is not None:
    debug.WriteTObject(hists, 'hist')
    for i, cont in enumerate(cont_1sigma):
        debug.WriteTObject(cont, 'cont_1sigma_%i' % i)
    for i, cont in enumerate(cont_2sigma):
        debug.WriteTObject(cont, 'cont_2sigma_%i' % i)

legend = plot.PositionedLegend(0.3, 0.2, 3, 0.015)

pads[0].cd()
axis.Draw()
for i, p in enumerate(cont_2sigma):
    p.SetLineStyle(1)
    p.SetLineWidth(2)
    p.SetLineColor(ROOT.kBlack)
    p.SetFillColor(ROOT.kBlue-10)
    p.SetFillStyle(1001)
    p.Draw("F SAME")
    p.Draw("L SAME")
    legend.AddEntry(cont_1sigma[0], "68% CL", "F")

for i, p in enumerate(cont_1sigma):
    p.SetLineStyle(1)
    p.SetLineWidth(2)
    p.SetLineColor(ROOT.kBlack)
    p.SetFillColor(ROOT.kBlue-8)
    p.SetFillStyle(1001)
    p.Draw("F SAME")
    p.Draw("L SAME")
    legend.AddEntry(cont_2sigma[0], "95% CL", "F")

best.Draw("P SAME")
legend.AddEntry(best, "Best fit", "P")


hmass=""
if (args.files.find(".mH") != -1):
    hmass = args.files[args.files.find(".mH")+3:args.files.find(".root")]
    legend.SetHeader("m_{#phi} = "+hmass+" GeV")
legend.Draw("same")

plot.DrawCMSLogo(pads[0], 'CMS', args.cms_sub, 11, 0.045, 0.035, 1.2, '', 1.0)
plot.DrawTitle(pads[0], args.title_right, 3)
plot.DrawTitle(pads[0], args.title_left, 1)
plot.FixOverlay()
canv.Print('.pdf')
canv.Print('.png')
canv.Close()

if debug is not None:
    debug.Close()
