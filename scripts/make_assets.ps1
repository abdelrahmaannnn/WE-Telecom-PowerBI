param([string]$LogoSrc, [string]$OutDir)
Add-Type -AssemblyName System.Drawing
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force $OutDir | Out-Null
$S = 2  # render at 2x for crispness (2560x1440)

function C([string]$hex, [int]$a = 255) {
  $h = $hex.TrimStart('#')
  [System.Drawing.Color]::FromArgb($a, [Convert]::ToInt32($h.Substring(0,2),16), [Convert]::ToInt32($h.Substring(2,2),16), [Convert]::ToInt32($h.Substring(4,2),16))
}
function RR([float]$x,[float]$y,[float]$w,[float]$h,[float]$r) {
  $p = New-Object System.Drawing.Drawing2D.GraphicsPath
  $d = $r*2
  $p.AddArc($x,$y,$d,$d,180,90); $p.AddArc($x+$w-$d,$y,$d,$d,270,90)
  $p.AddArc($x+$w-$d,$y+$h-$d,$d,$d,0,90); $p.AddArc($x,$y+$h-$d,$d,$d,90,90)
  $p.CloseFigure(); $p
}
function LG([float]$x,[float]$y,[float]$w,[float]$h,[string]$c1,[string]$c2,[float]$ang) {
  $r = New-Object System.Drawing.RectangleF $x,$y,$w,$h
  New-Object System.Drawing.Drawing2D.LinearGradientBrush $r, (C $c1), (C $c2), $ang
}
function NewCanvas {
  $bmp = New-Object System.Drawing.Bitmap (1280*$S), (720*$S)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'; $g.InterpolationMode = 'HighQualityBicubic'
  $g.ScaleTransform($S,$S)
  ,@($bmp,$g)
}
function Card($g,[float]$x,[float]$y,[float]$w,[float]$h,[float]$r=12,$fill=$null,[int]$shadow=1) {
  if ($shadow) { for ($i=6; $i -ge 1; $i--) { $sp = RR ($x-$i+1) ($y-$i+4) ($w+2*$i-2) ($h+2*$i-2) ($r+$i); $g.FillPath((New-Object System.Drawing.SolidBrush (C '#3E1F5C' 5)), $sp) } }
  $p = RR $x $y $w $h $r
  if ($fill -eq $null) { $fill = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White) }
  $g.FillPath($fill, $p)
}
function IconBubble($g,[float]$cx,[float]$cy,[float]$d,[string]$glyph,[string]$c1='#5B1F86',[string]$c2='#C13B9A') {
  $rect = New-Object System.Drawing.RectangleF ($cx-$d/2), ($cy-$d/2), $d, $d
  $br = New-Object System.Drawing.Drawing2D.LinearGradientBrush $rect, (C $c1), (C $c2), 45
  $g.FillEllipse($br, $rect)
  $f = New-Object System.Drawing.Font 'Segoe MDL2 Assets', ($d*0.42), ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
  $sf = New-Object System.Drawing.StringFormat; $sf.Alignment='Center'; $sf.LineAlignment='Center'
  $g.DrawString([string][char][Convert]::ToInt32($glyph,16), $f, [System.Drawing.Brushes]::White, $rect, $sf)
}
function Txt($g,[string]$t,[float]$x,[float]$y,[float]$size,[string]$color,[string]$font='Segoe UI',[string]$style='Regular',[int]$a=255) {
  $f = New-Object System.Drawing.Font $font, $size, ([System.Drawing.FontStyle]::$style), ([System.Drawing.GraphicsUnit]::Pixel)
  $g.DrawString($t, $f, (New-Object System.Drawing.SolidBrush (C $color $a)), $x, $y)
}

# ---------- Logo: crop to content, white -> transparent ----------
$src = [System.Drawing.Bitmap]::FromFile($LogoSrc)
$minX=$src.Width; $minY=$src.Height; $maxX=0; $maxY=0
for ($y=0; $y -lt $src.Height; $y+=1) { for ($x=0; $x -lt $src.Width; $x+=1) {
  $px = $src.GetPixel($x,$y)
  if (($px.R + $px.G + $px.B) -lt 720) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} }
}}
$pad=6; $minX=[Math]::Max(0,$minX-$pad); $minY=[Math]::Max(0,$minY-$pad); $maxX=[Math]::Min($src.Width-1,$maxX+$pad); $maxY=[Math]::Min($src.Height-1,$maxY+$pad)
$lw=$maxX-$minX+1; $lh=$maxY-$minY+1
$logo = New-Object System.Drawing.Bitmap $lw, $lh, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
for ($y=0; $y -lt $lh; $y++) { for ($x=0; $x -lt $lw; $x++) {
  $px = $src.GetPixel($x+$minX,$y+$minY)
  $m = [Math]::Min($px.R,[Math]::Min($px.G,$px.B))
  $alpha = [int][Math]::Max(0,[Math]::Min(255, (255-$m)*255/40))   # fade near-white to transparent
  if ($m -lt 215) { $alpha = 255 }
  $logo.SetPixel($x,$y,[System.Drawing.Color]::FromArgb($alpha,$px.R,$px.G,$px.B))
}}
$logo.Save("$OutDir\we_logo.png", [System.Drawing.Imaging.ImageFormat]::Png)
"logo ${lw}x${lh}"

function DrawLogo($g,[float]$cx,[float]$cy,[float]$maxW,[float]$maxH) {
  $k = [Math]::Min($maxW/$logo.Width, $maxH/$logo.Height)
  $w=$logo.Width*$k; $h=$logo.Height*$k
  $g.DrawImage($logo, [float]($cx-$w/2), [float]($cy-$h/2), [float]$w, [float]$h)
}

# ---------- HOME background ----------
$cv = NewCanvas; $bmp=$cv[0]; $g=$cv[1]
$full = New-Object System.Drawing.RectangleF 0,0,1280,720
$bg = New-Object System.Drawing.Drawing2D.LinearGradientBrush $full, (C '#1E0833'), (C '#7A2183'), 35
$blend = New-Object System.Drawing.Drawing2D.ColorBlend 3
$blend.Colors = @((C '#1A062E'), (C '#3F1466'), (C '#8E2A8C')); $blend.Positions = @(0, 0.55, 1)
$bg.InterpolationColors = $blend
$g.FillRectangle($bg, $full)
# soft glows
foreach ($c in @(@(1150,90,520,'#C13B9A',40), @(980,660,420,'#6E3FA3',45), @(120,700,360,'#C13B9A',22))) {
  $gp = New-Object System.Drawing.Drawing2D.GraphicsPath; $gp.AddEllipse([float]($c[0]-$c[2]/2),[float]($c[1]-$c[2]/2),[float]$c[2],[float]$c[2])
  $pb = New-Object System.Drawing.Drawing2D.PathGradientBrush $gp; $pb.CenterColor = C $c[3] $c[4]; $pb.SurroundColors = @((C $c[3] 0))
  $g.FillPath($pb,$gp)
}
# flowing flame-like curves
for ($i=0; $i -lt 14; $i++) {
  $pen = New-Object System.Drawing.Pen (C '#E58AD0' (10 + $i*3)), 1.4
  $g.DrawBezier($pen, [float](760+$i*14), 740, [float](900+$i*10), [float](520-$i*8), [float](1120-$i*6), [float](420+$i*4), [float](1300), [float](60+$i*16))
}
# dotted grid accent
for ($x=60; $x -le 220; $x+=16) { for ($y=60; $y -le 140; $y+=16) { $g.FillEllipse((New-Object System.Drawing.SolidBrush (C '#FFFFFF' 40)), $x, $y, 2.4, 2.4) } }

# logo card
Card $g 90 190 300 300 28
DrawLogo $g 240 340 210 230
# accent line under logo card
$g.FillRectangle((LG 90 510 300 4 '#C13B9A' '#6E3FA3' 0), 90, 510, 300, 4)

# headings
Txt $g 'TELECOM ANALYTICS' 452 160 14 '#F2A1D0' 'Segoe UI Semibold' 'Regular'
Txt $g 'Performance Dashboard' 448 182 46 '#FFFFFF' 'Segoe UI Semibold' 'Regular'
Txt $g 'Revenue  •  Customers  •  Churn  •  Network  •  Experience' 452 244 16 '#E9DDF3' 'Segoe UI' 'Regular' 220

# KPI glass tiles (cards placed on top in Power BI)
$tiles = @(@(450,'E8C7','Total Revenue'), @(695,'E716','Active Customers'), @(940,'E701','Network Availability'))
foreach ($t in $tiles) {
  $p = RR $t[0] 292 230 104 16
  $g.FillPath((New-Object System.Drawing.SolidBrush (C '#FFFFFF' 28)), $p)
  $g.DrawPath((New-Object System.Drawing.Pen (C '#FFFFFF' 70), 1), $p)
  IconBubble $g ($t[0]+36) 344 44 $t[1] '#C13B9A' '#F07CC4'
}

# Explore button
$bp = RR 450 430 270 56 28
$g.FillPath((LG 450 430 270 56 '#E04FA8' '#8E2A8C' 0), $bp)
Txt $g 'Revenue & Customers' 478 445 19 '#FFFFFF' 'Segoe UI Semibold' 'Regular'
$af = New-Object System.Drawing.Font 'Segoe MDL2 Assets', 16, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
$g.DrawString([string][char]0xE72A, $af, [System.Drawing.Brushes]::White, 680, 450)
$bp2 = RR 740 430 270 56 28
$g.FillPath((New-Object System.Drawing.SolidBrush (C '#FFFFFF' 30)), $bp2); $g.DrawPath((New-Object System.Drawing.Pen (C '#F2A1D0' 200), 1.5), $bp2)
Txt $g 'Network & Experience' 766 445 19 '#FFFFFF' 'Segoe UI Semibold' 'Regular'
$g.DrawString([string][char]0xE72A, $af, [System.Drawing.Brushes]::White, 972, 450)

Txt $g 'Data period: Jan 2024 – Dec 2025' 452 520 13 '#E9DDF3' 'Segoe UI' 'Regular' 170
# footer
$g.FillRectangle((New-Object System.Drawing.SolidBrush (C '#FFFFFF' 30)), 0, 676, 1280, 1)
Txt $g 'WE  |  Telecom Egypt  —  Business Performance Report' 40 688 12 '#FFFFFF' 'Segoe UI' 'Regular' 150
$bmp.Save("$OutDir\home_bg.png", [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
'home ok'

function DashBg([string]$title,[string]$sub,[string[]]$kpis,[string]$navText,[string]$navGlyph,[string]$file) {
$cv = NewCanvas; $bmp=$cv[0]; $g=$cv[1]
$g.FillRectangle((New-Object System.Drawing.SolidBrush (C '#F4F1F8')), 0, 0, 1280, 720)
$hr = New-Object System.Drawing.RectangleF 0,0,1280,64
$hb = New-Object System.Drawing.Drawing2D.LinearGradientBrush $hr, (C '#2A0B47'), (C '#8E2A8C'), 0
$g.FillRectangle($hb, $hr)
for ($i=0; $i -lt 8; $i++) { $g.DrawBezier((New-Object System.Drawing.Pen (C '#F2A1D0' (14+$i*4)), 1), [float](620+$i*20), 64, [float](700+$i*20), 20, [float](800+$i*14), 50, [float](900+$i*12), -4) }
Card $g 12 8 48 48 10 $null 0
DrawLogo $g 36 32 38 40
Txt $g $title 74 10 22 '#FFFFFF' 'Segoe UI Semibold' 'Regular'
Txt $g $sub 76 38 12 '#F2C6E6' 'Segoe UI' 'Regular'
$hf = New-Object System.Drawing.Font 'Segoe MDL2 Assets', 14, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
# page-switch pill
$np = RR 806 16 136 32 16
$g.FillPath((LG 806 16 136 32 '#E04FA8' '#B0308E' 0), $np)
$g.DrawString([string][char][Convert]::ToInt32($navGlyph,16), $hf, [System.Drawing.Brushes]::White, 820, 24)
Txt $g $navText 842 21 14 '#FFFFFF' 'Segoe UI Semibold' 'Regular'
# home pill
$hp = RR 1162 16 102 32 16
$g.FillPath((New-Object System.Drawing.SolidBrush (C '#FFFFFF' 40)), $hp); $g.DrawPath((New-Object System.Drawing.Pen (C '#FFFFFF' 110), 1), $hp)
$g.DrawString([string][char]0xE80F, $hf, [System.Drawing.Brushes]::White, 1180, 24)
Txt $g 'Home' 1202 21 14 '#FFFFFF' 'Segoe UI Semibold' 'Regular'
# slicer holder
$sp = RR 954 16 196 32 10
$g.FillPath((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)), $sp)
for ($i=0; $i -lt 6; $i++) {
  $x = 16 + $i*209.8
  Card $g $x 78 199 96 14
  $g.FillRectangle((LG $x 78 5 96 '#5B1F86' '#C13B9A' 90), $x, 92, 4, 68)
  IconBubble $g ($x+38) 126 44 $kpis[$i]
}
Card $g 16 186 780 266 14
Card $g 806 186 458 266 14
Card $g 16 462 410 246 14
Card $g 436 462 410 246 14
Card $g 856 462 408 246 14
$bmp.Save("$OutDir\$file", [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
"$file ok"
}
DashBg 'Revenue & Customer Overview' 'WE Telecom  •  Monthly performance' @('E8C7','EB11','EB05','E77B','E716','EB0F') 'Network' 'E701' 'dashboard_bg.png'
DashBg 'Network & Customer Experience' 'WE Telecom  •  Quality, service and acquisition' @('E701','E7BA','E717','E734','E76E','E73E') 'Revenue' 'E8C7' 'network_bg.png'
