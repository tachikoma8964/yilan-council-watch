import Vision
import ImageIO
import Foundation
let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let src = CGImageSourceCreateWithURL(url as CFURL, nil), let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else { exit(1) }
let req = VNRecognizeTextRequest()
req.recognitionLanguages = ["zh-Hant"]
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
for o in req.results ?? [] {
    guard let t = o.topCandidates(1).first else { continue }
    let b = o.boundingBox
    print(String(format: "%.4f\t%.4f\t%.4f\t%.4f\t%@", b.minX, 1 - b.maxY, b.width, b.height, t.string))
}
