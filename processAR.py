using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Drawing;
using System.Drawing.Imaging;
using System.Drawing.Drawing2D;
using System.Collections;
using System.Windows.Forms;



namespace tesKamera
{
    class UbahGambar
    {
        public Bitmap resizeImage(Image gambar, Size uk)
        {
            return (Bitmap)(new Bitmap(gambar, uk));
        }

        
        public int Width, Height;
        public int panjang, lebar, tinggi;
        public Bitmap Obj;
        public int[,] GreyImage;
        //Gaussian Kernel Data
        int[,] GaussianKernel;

        int KernelSize = 5;
        //Canny Edge Detection Parameters
        float MaxHysteresisThresh, MinHysteresisThresh;
        public float[,] DerivativeX;
        public float[,] DerivativeY;
        public int[,] FilteredImage;
        public float[,] Gradient;
        public float[,] NonMax;
        public int[,] PostHysteresis;
        int[,] EdgePoints;

        public int[,] EdgeMap;
 
        public ArrayList segmenx1;
        public ArrayList segmenx2;
        public ArrayList segmenY;

        public ArrayList horzx1;
        public ArrayList horzx2;
        public ArrayList horzy1;
        public ArrayList horzy2;


        public int[,] Canny(Bitmap Input)
        {
            MaxHysteresisThresh = 150;
            MinHysteresisThresh = 130;
            //KernelSize = 5;

            Obj = Input;
            Width = Obj.Width;
            Height = Obj.Height;

            EdgeMap = new int[Width, Height];


            Grayscaling();
            FilteredImage = GaussianFilter(GreyImage);
            DetectCannyEdges();


            segmenHorizontal();
            segmenVertikal();
            corner();
            return EdgeMap;
        }

        private void DetectCannyEdges()
        {
            Gradient = new float[Width, Height];
            NonMax = new float[Width, Height];
            PostHysteresis = new int[Width, Height];

            DerivativeX = new float[Width, Height];
            DerivativeY = new float[Width, Height];

            int[,] Dy = new int[,] { { -1, -2, -1 }, { 0, 0, 0 }, { 1, 2, 1 } };
            int[,] Dx = new int[,] { { -1, 0, 1 }, { -2, 0, 2 }, { -1, 0, 1 } };


            DerivativeX = Differentiate(FilteredImage, Dx);
            DerivativeY = Differentiate(FilteredImage, Dy);

            int i, j;

            //Compute the gradient magnitude based on derivatives in x and y:
            for (i = 0; i <= (Width - 1); i++)
            {
                for (j = 0; j <= (Height - 1); j++)
                {
                    Gradient[i, j] = (float)Math.Sqrt((DerivativeX[i, j] * DerivativeX[i, j]) + (DerivativeY[i, j] * DerivativeY[i, j]));

                }

            }

            // Perform Non maximum suppression:
            // NonMax = Gradient;

            for (i = 0; i <= (Width - 1); i++)
            {
                for (j = 0; j <= (Height - 1); j++)
                {
                    NonMax[i, j] = Gradient[i, j];
                }
            }



            int Limit = KernelSize / 2;
            int r, c;
            float Tangent;

            for (i = Limit; i <= (Width - Limit) - 1; i++)
            {
                for (j = Limit; j <= (Height - Limit) - 1; j++)
                {

                    if (DerivativeX[i, j] == 0)
                        Tangent = 90F;
                    else
                        Tangent = (float)(Math.Atan(DerivativeY[i, j] / DerivativeX[i, j]) * 180 / Math.PI); //rad to degree

                    if (Tangent < 0)
                        Tangent = 180 + Tangent;

                    //Horizontal Edge
                    if (((0 < Tangent) && (Tangent <= 22.5)) || ((157.5 < Tangent) && (Tangent <= 180)))
                    {
                        if ((Gradient[i, j] < Gradient[i, j + 1]) || (Gradient[i, j] < Gradient[i, j - 1]))
                            NonMax[i, j] = 0;

                    }


                    //Vertical Edge
                    if (((67.5 < Tangent) && (Tangent <= 112.5)))
                    {
                        if ((Gradient[i, j] < Gradient[i + 1, j]) || (Gradient[i, j] < Gradient[i - 1, j]))
                            NonMax[i, j] = 0;

                    }

                    //diagonal bawah
                    if (((112.5 < Tangent) && (Tangent <= 157.5)))
                    {
                        if ((Gradient[i, j] < Gradient[i + 1, j - 1]) || (Gradient[i, j] < Gradient[i - 1, j + 1]))
                            NonMax[i, j] = 0;

                    }

                    //diagonal atas
                    if (((22.5 < Tangent) && (Tangent <= 67.5)))
                    {
                        if ((Gradient[i, j] < Gradient[i + 1, j + 1]) || (Gradient[i, j] < Gradient[i - 1, j - 1]))
                            NonMax[i, j] = 0;

                    }

                }
            }


          
            for (r = 0; r <= Width - 1; r++)
            {
                for (c = 0; c <= Height - 1; c++)
                {

                    PostHysteresis[r, c] = (int)NonMax[r, c];
                   
                }

            }

          


            EdgePoints = new int[Width, Height];

            for (r = Limit; r <= (Width - Limit) - 1; r++)
            {
                for (c = Limit; c <= (Height - Limit) - 1; c++)
                {
                    if (PostHysteresis[r, c] >= MaxHysteresisThresh)
                    {
                        EdgePoints[r, c] = 1;
                    }
                    if ((PostHysteresis[r, c] < MinHysteresisThresh))
                    {
                        EdgePoints[r, c] = 0;
                    }

                }

            }

            HysterisisThresholding(EdgePoints);


            return;


        }

        private void HysterisisThresholding(int[,] Edges)
        {

            int i, j;
            int Limit = KernelSize / 2;



            for (i = Limit; i <= (Width - 1) - Limit; i++)
            {
                for (j = Limit; j <= (Height - 1) - Limit; j++)
                {
                    if (Edges[i, j] == 1)
                    {
                        //EdgeMap[i, j] = 1*255;
                        EdgeMap[i, j] = 1 * 0;
                    }
                    else
                    {
                        EdgeMap[i, j] = GreyImage[i, j];
                        //EdgeMap[i, j] = 0;
                    }
                }
            }

            return;
        }



        private float[,] Differentiate(int[,] Data, int[,] Filter)
        {
            int i, j, k, l, Fh, Fw;

            Fw = Filter.GetLength(0);
            Fh = Filter.GetLength(1);
            float sum = 0;
            float[,] Output = new float[Width, Height];

            for (i = Fw / 2; i <= (Width - Fw / 2) - 1; i++)
            {
                for (j = Fh / 2; j <= (Height - Fh / 2) - 1; j++)
                {
                    sum = 0;
                    for (k = -Fw / 2; k <= Fw / 2; k++)
                    {
                        for (l = -Fh / 2; l <= Fh / 2; l++)
                        {
                            sum = sum + Data[i + k, j + l] * Filter[Fw / 2 + k, Fh / 2 + l];


                        }
                    }
                    Output[i, j] = sum;

                }

            }
            return Output;

        }

        private float[,] Differentiate2(int[,] Data, int[,] Filter, int width, int height)
        {
            int i, j, k, l, Fh, Fw;

            Fw = Filter.GetLength(0);
            Fh = Filter.GetLength(1);
            float sum = 0;
            float[,] Output = new float[width, height];

            for (i = Fw / 2; i <= (width - Fw / 2) - 1; i++)
            {
                for (j = Fh / 2; j <= (height - Fh / 2) - 1; j++)
                {
                    sum = 0;
                    for (k = -Fw / 2; k <= Fw / 2; k++)
                    {
                        for (l = -Fh / 2; l <= Fh / 2; l++)
                        {
                            sum = sum + Data[i + k, j + l] * Filter[Fw / 2 + k, Fh / 2 + l];


                        }
                    }
                    Output[i, j] = sum;

                }

            }
            return Output;

        }

        private void Grayscaling()
        {
            int i, j;
            GreyImage = new int[Obj.Width, Obj.Height];  //[Row,Column]
            Bitmap image = Obj;
            BitmapData bitmapData1 = image.LockBits(new Rectangle(0, 0, image.Width, image.Height),
                                     ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            unsafe
            {
                byte* imagePointer1 = (byte*)bitmapData1.Scan0;

                for (i = 0; i < bitmapData1.Height; i++)
                {
                    for (j = 0; j < bitmapData1.Width; j++)
                    {                 
                        GreyImage[j, i] = (int)(imagePointer1[0] * 0.11 + imagePointer1[1] * 0.59 + imagePointer1[2] * 0.3);
                        //4 bytes per pixel
                        imagePointer1 += 4;
                    }//end for j
                    //4 bytes per pixel
                    imagePointer1 += bitmapData1.Stride - (bitmapData1.Width * 4);
                }//end for i
            }//end unsafe
            image.UnlockBits(bitmapData1);

            return;
        }

        private int[,] GaussianFilter(int[,] Data)
        {
            GaussianKernel = new int[,] {
                {1,4,7,4,1},
                {4,20,33,20,4},
                {7,33,55,33,7},
                {4,20,33,20,4},
                {1,4,7,4,1}
            };


            int[,] Output = new int[Width, Height];
            int i, j, k, l;
            int Limit = KernelSize / 2;

            float Sum = 0;


            Output = Data;


            for (i = Limit; i <= ((Width - 1) - Limit); i++)
            {
                for (j = Limit; j <= ((Height - 1) - Limit); j++)
                {
                    Sum = 0;
                    for (k = -Limit; k <= Limit; k++)
                    {

                        for (l = -Limit; l <= Limit; l++)
                        {
                            Sum = Sum + ((float)Data[i + k, j + l] * GaussianKernel[Limit + k, Limit + l]);

                        }
                    }
                    Output[i, j] = (int)(Math.Round(Sum / 331));
                }

            }


            return Output;
        }





        int besarSegmen = 5;

        public void segmenHorizontal()
        {

             segmenx1 = new ArrayList();
             segmenx2 = new ArrayList();
             segmenY = new ArrayList();

        horzx1 = new ArrayList();
        horzx2 = new ArrayList();
        horzy1 = new ArrayList();
        horzy2 = new ArrayList();




        int i = 0, j = 0, flag = 0;
        int x1 = 0, x2, y = 0;

        while (i < EdgeMap.GetLength(1) - 1)
        {

            flag = 0;
            j = 0;

            while (j < EdgeMap.GetLength(0) - 1)
            {
                // Console.WriteLine("nilai pixel:( " + j + ", " + i + "): " + EdgeMap[j, i]);
                if (flag == 0)
                {
                    if (EdgeMap[j, i] == 0)
                    {
                        flag = 1;
                        x1 = j;
                        y = i;

                    }
                    j++;
                }
                else if (flag == 1)
                {
                    if (EdgeMap[j, i] == 0)
                    {
                        j++;
                    }
                    else
                        flag = 2;

                }
                else
                {
                    x2 = j - 1;
                    if (x2 > x1)
                    {
                        // Console.WriteLine("counter: " + counter);
                        /*segmenx1[counter] = x1;
                        segmenx2[counter] = x2;
                        segmenY[counter] = y;
                        counter++;*/

                        segmenx1.Add(x1);
                        segmenx2.Add(x2);
                        segmenY.Add(y);

                    }
                    flag = 0;
                    j++;
                }

            }

            i++;
        }


        i = 0; j = 0;
        int setx1 = 0, sety1 = 0, indeks = 0, temp = 0, setx2 = 0;
        while (i < segmenY.Count)
        {
            j = i + 1;
            setx2 = (int)segmenx2[i];
            sety1 = (int)segmenY[i];
            temp = 0;
           
            while (j < segmenY.Count)
            {


                if ((int)segmenY[j] - sety1 > 1)
                {

                    break;
                }
                if (temp == 0)
                {
                    if ((int)segmenY[j] == sety1 + 1 && (int)segmenY[j] != -1)
                    {

                        if ((int)segmenx1[i] - (int)segmenx2[j] < 2 && (int)segmenx1[i] - (int)segmenx2[j] >= 0)
                        {
                            xx1 = setx2;
                            yy1 = sety1;
                            sety1++;

                            segmenY[i] = -1;

                            temp = 1;
                            indeks = j;

                        }

                    }

                    j++;
                }
                else
                {
                    if ((int)segmenY[j] == sety1 + 1 && (int)segmenx1[indeks] - (int)segmenx2[j] < 2 && (int)segmenx1[indeks] - (int)segmenx2[j] >= 0 && (int)segmenY[j] != -1)
                    {
                        sety1++;

                        segmenY[indeks] = -1;
                        indeks = j;
                    }

                    j++;
                    if (j >= segmenY.Count)
                        break;
                    if ((int)segmenY[j] - sety1 > 1)
                    {

                        if (xx1 - (int)segmenx1[indeks] > besarSegmen)
                        {
                            /*horzx2[counter2] = xx1;
                            horzy2[counter2] = yy1;
                            horzx1[counter2] = segmenx1[indeks];
                            horzy1[counter2] = segmenY[indeks];
                            counter2++;*/

                            horzx2.Add(xx1);
                            horzy2.Add(yy1);
                            horzx1.Add(segmenx1[indeks]);
                            horzy1.Add(segmenY[indeks]);
                            segmenY[j] = -1;



                        }

                        break;
                    }
                }

            }
            i++;
        }


        i = 0; j = 0;
        setx1 = 0; sety1 = 0; indeks = 0; temp = 0;
        while (i < segmenY.Count)
        {
            j = i + 1;
            setx1 = (int)segmenx1[i];
            sety1 = (int)segmenY[i];
            temp = 0;


            indeks = 0;
            while (j < segmenY.Count)
            {

                if ((int)segmenY[j] - sety1 > 1)
                    break;

                if (temp == 0)
                {

                    if ((int)segmenY[j] == sety1 + 1 && (int)segmenY[j] != -1)
                    {

                        if ((int)segmenx1[j] - (int)segmenx2[i] < 2 && (int)segmenx1[j] - (int)segmenx2[i] >= 0)
                        {
                            xx1 = setx1;
                            yy1 = sety1;
                            sety1++;
                            segmenY[i] = -1;
                            temp = 1;
                            indeks = j;
                        }

                    }

                    j++;
                }
                else
                {
                    if ((int)segmenY[j] == sety1 + 1 && (int)segmenx1[j] - (int)segmenx2[indeks] < 2 && (int)segmenx1[j] - (int)segmenx2[indeks] >= 0 && (int)segmenY[j] != -1)
                    {
                        sety1++;
                        segmenY[indeks] = -1;
                        indeks = j;
                    }

                    j++;
                    if (j >= segmenY.Count)
                        break;
                    if ((int)segmenY[j] - sety1 > 1)
                    {

                        if ((int)segmenx2[indeks] - xx1 > besarSegmen)
                        {
                            
                            horzx1.Add(xx1);
                            horzy1.Add(yy1);
                            horzx2.Add(segmenx2[indeks]);
                            horzy2.Add(segmenY[indeks]);

                            segmenY[j] = -1;
                        }
                        break;
                    }
                }

            }

            i++;

        }
           
            
        }


        public ArrayList segmeny1;
        public ArrayList segmeny2;
        public ArrayList segmenx;

        public ArrayList diagx1;
        public ArrayList diagy1;
        public ArrayList diagx2;
        public ArrayList diagy2;

        public void segmenVertikal()
        {
            segmeny1 = new ArrayList();
            segmeny2 = new ArrayList();
            segmenx = new ArrayList();

            diagx1 = new ArrayList();
            diagy1 = new ArrayList();
            diagx2 = new ArrayList();
            diagy2 = new ArrayList();

            int y1 = 0, y2 = 0, x = 0, flag = 0, temp = 0;
            int i = 0, j = 0;
            while (i < EdgeMap.GetLength(0) - 1)
            {
                j = 0;
                flag = 0;
                while (j < EdgeMap.GetLength(1) - 1)
                {

                    if (flag == 0)
                    {
                        if (EdgeMap[i, j] == 0)
                        {
                            flag = 1;
                            y1 = j;
                            x = i;
                        }
                        j++;
                    }
                    else if (flag == 1)
                    {
                        if (EdgeMap[i, j] == 0)
                        {
                            j++;
                        }
                        else
                            flag = 2;
                    }
                    else
                    {
                        y2 = j - 1;

                        if (y2 > y1)
                        {
                            //temp = 0;
                            
                            segmeny1.Add(y1);
                            segmeny2.Add(y2);
                            segmenx.Add(x);
                            
                        }
                        flag = 0;
                        j++;
                    }

                }
                i++;

            }




            i = 0; j = 0;
            int setx1 = (int)segmenx[i], sety1 = 0, indeks = 0;
            while (i < segmenx.Count)
            {

                j = i + 1;
                setx1 = (int)segmenx[i];
                sety1 = (int)segmeny1[i];
                temp = 0;
                while (j < segmenx.Count)
                {

                    if ((int)segmenx[j] - setx1 > 1)
                    {
                        break;
                    }

                    if (temp == 0)
                    {
                        if ((int)segmenx[j] == (int)setx1 + 1 && (int)segmenx[j] != -1)
                        {
                            if ((int)segmeny1[j] - (int)segmeny2[i] < 2 && (int)segmeny1[j] - (int)segmeny2[i] >= 0)
                            {
                                xx1 = setx1;
                                setx1++;
                                yy1 = sety1;

                                segmenx[i] = -1;
                                temp = 1;
                                indeks = j;
                            }


                        }

                        j++;

                    }
                    else
                    {
                        if (Convert.ToInt16(segmenx[j]) == setx1 + 1 && (int)segmeny1[j] - (int)segmeny2[indeks] < 2 && (int)segmeny1[j] - (int)segmeny2[indeks] >= 0 && (int)segmenx[j] != -1)
                        {

                            segmenx[indeks] = -1;
                            indeks = j;
                            setx1++;

                        }


                        j++;

                        if (j >= segmenx.Count)
                            break;
                        if ((int)segmenx[j] - setx1 > 1)
                        {
                            if ((int)segmeny2[indeks] - yy1 > besarSegmen)
                            {
                                diagx1.Add(xx1);
                                diagy1.Add(yy1);
                                diagx2.Add(segmenx[indeks]);
                                diagy2.Add(segmeny2[indeks]);
                            }

                            segmenx[j] = -1;


                            break;
                        }
                    }
                }

                i++;


            }

            i = 0; j = 0;
            int sety2 = 0;
            setx1 = (int)segmenx[i]; indeks = 0;
            while (i < segmenx.Count)
            {

                j = i + 1;
                setx1 = (int)segmenx[i];
                sety2 = (int)segmeny2[i];
                temp = 0;

                while (j < segmenx.Count)
                {

                    // Console.WriteLine("j: " + j);
                    if ((int)segmenx[j] - setx1 > 1)
                    {

                        break;
                    }
                    if (temp == 0)
                    {
                        if ((int)segmenx[j] == (int)setx1 + 1 && (int)segmenx[j] != -1)
                        {

                            if ((int)segmeny1[i] - (int)segmeny2[j] < 2 && (int)segmeny1[i] - (int)segmeny2[j] >= 0)
                            {
                                xx1 = setx1;
                                setx1++;
                                yy1 = sety2;

                                segmenx[i] = -1;
                                temp = 1;
                                indeks = j;
                            }


                        }
                        // else
                        j++;
                    }
                    else
                    {
                        if (Convert.ToInt16(segmenx[j]) == setx1 + 1 && (int)segmeny1[indeks] - (int)segmeny2[j] < 2 && (int)segmeny1[indeks] - (int)segmeny2[j] >= 0 && (int)segmenx[j] != -1)
                        {

                            segmenx[indeks] = -1;
                            indeks = j;
                            setx1++;

                        }

                        j++;

                        if (j >= segmenx.Count)
                        {

                            break;
                        }
                        if ((int)segmenx[j] - setx1 > 1)
                        {

                            if (yy1 - (int)segmeny1[indeks] > besarSegmen)
                            {
                                diagx1.Add(segmenx[indeks]);
                                diagy1.Add(segmeny1[indeks]);
                                diagx2.Add(xx1);
                                diagy2.Add(yy1);

                            }

                         
                            break;
                        }
                    }
                }
               
                i++;
                
            }

           

        }



        public ArrayList cornerx1;
        public ArrayList cornery1;
        public ArrayList cornerx2;
        public ArrayList cornery2;
        public ArrayList cornerx3;
        public ArrayList cornery3;
        public ArrayList cornerx4;
        public ArrayList cornery4;

        public void corner()
        {
            cornerx1 = new ArrayList();
            cornery1 = new ArrayList();
            cornerx2 = new ArrayList();
            cornery2 = new ArrayList();
            cornerx3 = new ArrayList();
            cornery3 = new ArrayList();
            cornerx4 = new ArrayList();
            cornery4 = new ArrayList();

            int i = 0, j = 0;
            int kiri, atas, kanan, bawah;
            int max = 0, min = 10000;
            while (i < horzx1.Count)
            {
                int horx2 = Convert.ToInt32(horzx2[i]);
                int hory2 = Convert.ToInt32(horzy2[i]);
                int horx1 = Convert.ToInt32(horzx1[i]);
                int hory1 = Convert.ToInt16(horzy1[i]);
                j = 0;

                while (j < diagx1.Count)
                {

                    int very1 = Convert.ToInt16(diagy1[j]);
                    int very2 = Convert.ToInt16(diagy2[j]);
                    int verx1 = (int)diagx1[j];
                    int verx2 = (int)diagx2[j];


                    if (Math.Abs(horx1 - verx1) < 5)
                    {

                        if (Math.Abs(very1 - hory1) < 5)
                        {
                            if (horx1 - 5 >= 0 && very1 - 5 >= 0 && horx1 + 5 < 360 && very1 + 5 < 240)
                            {
                                kiri = EdgeMap[horx1 - 5, very1]; //kiri
                                atas = EdgeMap[horx1, very1 - 5]; //atas
                                kanan = EdgeMap[horx1 + 5, very1]; //kanan
                                bawah = EdgeMap[horx1, very1 + 5]; //bawah

                                max = 0; min = 10000;


                                for (int p = very1 - 5; p <= very1 + 5; p++)
                                {
                                    for (int q = horx1 - 5; q <= horx1 + 5; q++)
                                    {
                                        if (EdgeMap[q, p] > max)
                                            max = EdgeMap[q, p];
                                        if (EdgeMap[q, p] < min)
                                            min = EdgeMap[q, p];

                                    }
                                }

                                double rata = min + max / 2;


                                if (kiri > rata && atas > rata && bawah < rata && kanan < rata)
                                {

                                    cornerx1.Add(horx1 - 1);
                                    cornery1.Add(very1 - 1);

                                }
                                else if (kiri > rata && atas > rata && bawah < rata && kanan > rata)
                                {
                                    cornerx1.Add(horx1 - 1);
                                    cornery1.Add(very1 - 1);
                                }
                                else if (kiri > rata && atas > rata && bawah > rata && kanan < rata)
                                {
                                    cornerx1.Add(horx1 - 1);
                                    cornery1.Add(very1 - 1);
                                }
                            }
                        }
                    }

                    if (Math.Abs(horx1 - verx2) < 5)
                    {

                        if (Math.Abs(hory1 - very2) < 5)
                        {
                            if (horx1 - 5 >= 0 && very2 - 5 >= 0 && horx1 + 5 < 360 && very2 + 5 < 240)
                            {
                                kiri = EdgeMap[horx1 - 5, very2]; //kiri
                                atas = EdgeMap[horx1, very2 - 5]; //atas
                                kanan = EdgeMap[horx1 + 5, very2]; //kanan
                                bawah = EdgeMap[horx1, very2 + 5]; //bawah
                                max = 0; min = 10000;

                                for (int p = very2 - 5; p <= very2 + 5; p++)
                                {
                                    for (int q = horx1 - 5; q <= horx1 + 5; q++)
                                    {
                                        if (EdgeMap[q, p] > max)
                                            max = EdgeMap[q, p];
                                        if (EdgeMap[q, p] < min)
                                            min = EdgeMap[q, p];

                                    }
                                }

                                double rata = min + max / 2;



                                if (kiri > rata && atas < rata && bawah > rata && kanan < rata)
                                {

                                    cornerx3.Add(horx1 - 1);
                                    cornery3.Add(very2 + 1);

                                }
                                else if (kiri > rata && atas > rata && bawah > rata && kanan < rata)
                                {
                                    cornerx3.Add(horx1 - 1);
                                    cornery3.Add(very2 + 1);
                                }
                                else if (kiri > rata && atas < rata && bawah > rata && kanan > rata)
                                {
                                    cornerx3.Add(horx1 - 1);
                                    cornery3.Add(very2 + 1);
                                }
                            }
                        }


                    }

                    if (Math.Abs(verx1 - horx2) < 5)
                    {
                        if (Math.Abs(very1 - hory2) < 5)
                        {


                            if (horx2 - 5 >= 0 && very1 - 5 >= 0 && horx2 + 5 < 360 && very1 + 5 < 240)
                            {
                                kanan = EdgeMap[horx2 + 5, very1];
                                bawah = EdgeMap[horx2, very1 + 5];
                                kiri = EdgeMap[horx2 - 5, very1];
                                atas = EdgeMap[horx2, very1 - 5];

                                max = 0; min = 10000;

                                for (int p = very1 - 5; p <= very1 + 5; p++)
                                {
                                    for (int q = horx2 - 5; q <= horx2 + 5; q++)
                                    {
                                        if (EdgeMap[q, p] > max)
                                            max = EdgeMap[q, p];
                                        if (EdgeMap[q, p] < min)
                                            min = EdgeMap[q, p];
                                    }
                                }

                                double rata = min + max / 2;


                                if (kiri < rata && atas > rata && bawah < rata && kanan > rata)
                                {

                                   
                                    cornerx2.Add(horx2 + 1);
                                    cornery2.Add(very1 - 1);

                                }
                                else if (kiri < rata && atas > rata && bawah > rata && kanan > rata)
                                {
                                    cornerx2.Add(horx2 + 1);
                                    cornery2.Add(very1 - 1);
                                }
                                else if (kiri > rata && atas > rata && bawah < rata && kanan > rata)
                                {
                                    cornerx2.Add(horx2 + 1);
                                    cornery2.Add(very1 - 1);
                                }
                            }

                        }


                    }
                    if (Math.Abs(verx2 - horx2) < 5)
                    {
                        if (Math.Abs(hory2 - very2) < 5)
                        {
                            if (horx2 - 5 >= 0 && very2 - 5 >= 0 && horx2 + 5 < 360 && very2 + 5 < 240)
                            {
                                kanan = EdgeMap[horx2 + 5, very2];
                                bawah = EdgeMap[horx2, very2 + 5];
                                kiri = EdgeMap[horx2 - 5, very2];
                                atas = EdgeMap[horx2, very2 - 5];


                                max = 0; min = 10000;

                                for (int p = very2 - 5; p <= very2 + 5; p++)
                                {
                                    for (int q = horx2 - 5; q <= horx2 + 5; q++)
                                    {
                                        if (EdgeMap[q, p] > max)
                                            max = EdgeMap[q, p];
                                        if (EdgeMap[q, p] < min)
                                            min = EdgeMap[q, p];


                                    }
                                }

                                double rata = min + max / 2;



                                if (kiri < rata && atas < rata && bawah > rata && kanan > rata)
                                {
                                   
                                    cornerx4.Add(horx2 + 1);
                                    cornery4.Add(very2 + 1);

                                }
                                else if (kiri < rata && atas > rata && bawah > rata && kanan > rata)
                                {
                                    cornerx4.Add(horx2 + 1);
                                    cornery4.Add(very2 + 1);
                                }
                                else if (kiri > rata && atas < rata && bawah > rata && kanan > rata)
                                {
                                    cornerx4.Add(horx2 + 1);
                                    cornery4.Add(very2 + 1);
                                }
                            }

                        }



                    }

                    j++;
                }
                i++;
            }

           
        }

      

        public ArrayList sisix1;
        public ArrayList sisiy1;
        public ArrayList sisix2;
        public ArrayList sisiy2;
        public ArrayList sisix3;
        public ArrayList sisiy3;
        public ArrayList sisix4;
        public ArrayList sisiy4;

        public ArrayList sidex1;
        public ArrayList sidey1;
        public ArrayList sidex2;
        public ArrayList sidey2;
        public ArrayList sidex3;
        public ArrayList sidey3;
        public ArrayList sidex4;
        public ArrayList sidey4;


        public ArrayList gradien1;
        public ArrayList gradien2;

        //public ArrayList panjang1;
        //public ArrayList panjang2;

        public int indeks1 = 0, indeks2 = 0;


        public int xx1 = 0, yy1 = 0, xx2 = 0, yy2 = 0, xx3 = 0, yy3 = 0, xx4 = 0, yy4 = 0;

        public int[,] hasil; 

        public int[,] segiEmpat()
        {
            hasil = new int[5, 2];

            sisix1 = new ArrayList();
            sisiy1 = new ArrayList();
            sisix2 = new ArrayList();
            sisiy2 = new ArrayList();
            sisix3 = new ArrayList();
            sisiy3 = new ArrayList();
            sisix4 = new ArrayList();
            sisiy4 = new ArrayList();

            sidex1 = new ArrayList();
            sidey1 = new ArrayList();
            sidex2 = new ArrayList();
            sidey2 = new ArrayList();
            sidex3 = new ArrayList();
            sidey3 = new ArrayList();
            sidex4 = new ArrayList();
            sidey4 = new ArrayList();

            gradien1 = new ArrayList();
            gradien2 = new ArrayList();
            int i = 0, j = 0;

            while (i < cornerx1.Count)
            {
                j = 0;
                double kornerx1 = Convert.ToDouble(cornerx1[i]);
                while (j < cornerx2.Count)
                {
                    double kornerx2 = Convert.ToDouble(cornerx2[j]);
                    if (kornerx1 < kornerx2 && kornerx2 - kornerx1 > 10)
                    {
                        sisix1.Add(cornerx1[i]);
                        sisiy1.Add(cornery1[i]);
                        sisix2.Add(cornerx2[j]);
                        sisiy2.Add(cornery2[j]);
                        double m = ((Convert.ToDouble(cornery2[j]) - Convert.ToDouble(cornery1[i])) / (kornerx2 - kornerx1));
                        gradien1.Add(m);
                        //double p = (kornerx2 - kornerx1);
                        //panjang1.Add(p);

                    }
                    j++;
                }
                i++;
            }

            i = 0; j = 0;
            while (i < cornerx3.Count)
            {
                j = 0;
                double kornerx3 = Convert.ToDouble(cornerx3[i]);
                double kornery3 = Convert.ToDouble(cornery3[i]);
                while (j < cornerx4.Count)
                {
                    double kornerx4 = Convert.ToDouble(cornerx4[j]);
                    if (kornerx3 < kornerx4 && kornerx4 - kornerx3 > 10)
                    {
                        sisix3.Add(cornerx3[i]);
                        sisiy3.Add(cornery3[i]);
                        sisix4.Add(cornerx4[j]);
                        sisiy4.Add(cornery4[j]);
                        double m = ((Convert.ToDouble(cornery4[j]) - Convert.ToDouble(cornery3[i])) / (kornerx4 - kornerx3));
                        gradien2.Add(m);
                        //double p = (kornerx4 - kornerx3);
                        //panjang2.Add(p);

                    }
                    j++;
                }
                i++;
            }

            
           

            i = 0; j = 0;
            indeks1 = 0; indeks2 = 0;
            double temp = 1000.00,temp2=1000.00;

            while (i < gradien1.Count)
            {
                j = 0;

                while (j < gradien2.Count)
                {

                    double selisih = Math.Abs(Convert.ToDouble(gradien1[i]) - Convert.ToDouble(gradien2[j]));
                    double lebar1 = Convert.ToDouble(sisiy3[j]) - Convert.ToDouble(sisiy1[i]);

                    double gradien3 = (Convert.ToDouble(sisix3[j]) - Convert.ToDouble(sisix1[i])) / (Convert.ToDouble(sisiy3[j]) - Convert.ToDouble(sisiy1[i]));
                    double gradien4 = (Convert.ToDouble(sisix4[j]) - Convert.ToDouble(sisix2[i])) / (Convert.ToDouble(sisiy4[j]) - Convert.ToDouble(sisiy2[i]));
                    double selisih2 = Math.Abs(gradien3 - gradien4);

                   

                    if (selisih < temp && selisih < 1 && selisih2 < temp2 && selisih2 < 1 && (int)sisiy1[i] < (int)sisiy3[j] && (int)sisiy2[i] < (int)sisiy4[j] && lebar1 > 10)
                    {

                        indeks1 = i;
                        indeks2 = j;
                        temp = selisih;
                        temp2 = selisih2;
                    }
                    j++;
                }

                i++;
            }

            if (temp != 1000)
            {


                xx1 = Convert.ToInt16(sisix1[indeks1]);
                yy1 = Convert.ToInt16(sisiy1[indeks1]);

                xx2 = Convert.ToInt16(sisix2[indeks1]);
                yy2 = Convert.ToInt16(sisiy2[indeks1]);

                xx3 = Convert.ToInt16(sisix3[indeks2]);
                yy3 = Convert.ToInt16(sisiy3[indeks2]);

                xx4 = Convert.ToInt16(sisix4[indeks2]);
                yy4 = Convert.ToInt16(sisiy4[indeks2]);

            }
            else
            {
 
                
                i = 0; j = 0;
                while (i < cornerx1.Count)
                {
                    j = 0;
                    while (j < cornerx3.Count)
                    {
                        if ((int)cornery1[i] < (int)cornery3[j] && (int)cornery3[j] - (int)cornery1[i] > 5)
                        {
                            sidex1.Add(cornerx1[i]);
                            sidey1.Add(cornery1[i]);
                            sidex3.Add(cornerx3[j]);
                            sidey3.Add(cornery3[j]);
                            //double m = ((Convert.ToDouble(cornery3[j]) - Convert.ToDouble(cornery1[i])) / (Convert.ToDouble(cornerx3[j]) - Convert.ToDouble(cornerx1[i])));
                            //gradien3.Add(m);
                        }
                        j++;
                    }
                    i++;
                }

                i = 0; j = 0;
                while (i < cornerx2.Count)
                {
                    j = 0;
                    while (j < cornerx4.Count)
                    {
                        if ((int)cornery2[i] < (int)cornery4[j] && (int)cornery4[j] - (int)cornery2[i] > 5)
                        {
                            sidex2.Add(cornerx2[i]);
                            sidey2.Add(cornery2[i]);
                            sidex4.Add(cornerx4[j]);
                            sidey4.Add(cornery4[j]);
                            //double m = ((Convert.ToDouble(cornery4[j]) - Convert.ToDouble(cornery2[i])) / (Convert.ToDouble(cornerx4[j]) - Convert.ToDouble(cornerx2[i])));
                            //gradien4.Add(m);
                        }
                        j++;
                    }
                    i++;
                }

               

                indeks1 = 0; indeks2 = 0;
                temp = 1000.00;
                i = 0; j = 0;

                while (i < sisix1.Count)
                {
                    j = 0;
                    while (j < sidex1.Count)
                    {
                        if ((int)sisix1[i] == (int)sidex1[j])
                        {

                            indeks1 = i;
                            indeks2 = j;
                            if (Convert.ToInt16(sisix2[indeks1]) > Convert.ToInt16(sidex3[indeks2]) && Convert.ToInt16(sisiy2[indeks1]) < Convert.ToInt16(sidey3[indeks2]))
                            {
                                temp = 0;
                                break;
                            }

                        }
                        j++;
                    }
                    if (temp == 0)
                        break;
                    i++;
                }
                if (temp == 0)
                {
                    
                    xx1 = Convert.ToInt16(sisix1[indeks1]);
                    yy1 = Convert.ToInt16(sisiy1[indeks1]);

                    xx2 = Convert.ToInt16(sisix2[indeks1]);
                    yy2 = Convert.ToInt16(sisiy2[indeks1]);

                    xx3 = Convert.ToInt16(sidex3[indeks2]);
                    yy3 = Convert.ToInt16(sidey3[indeks2]);

                    xx4 = xx2;
                    yy4 = yy3;

                   

                }
                else
                {
                    i = 0; j = 0;
                    while (i < sisix2.Count)
                    {
                        j = 0;
                        while (j < sidex2.Count)
                        {
                            if ((int)sisix2[i] == (int)sidex2[j])
                            {

                                indeks1 = i;
                                indeks2 = j;
                                if (Convert.ToInt16(sisix1[indeks1]) < Convert.ToInt16(sidex4[indeks2]) && Convert.ToInt16(sisiy1[indeks1]) < Convert.ToInt16(sidey4[indeks2]))
                                {
                                    temp = 0;
                                    break;
                                }

                            }
                            j++;
                        }
                        if (temp == 0)
                            break;
                        i++;
                    }
                    if (temp == 0)
                    {
                        
                        xx1 = Convert.ToInt16(sisix1[indeks1]);
                        yy1 = Convert.ToInt16(sisiy1[indeks1]);

                        xx2 = Convert.ToInt16(sisix2[indeks1]);
                        yy2 = Convert.ToInt16(sisiy2[indeks1]);

                        xx4 = Convert.ToInt16(sidex4[indeks2]);
                        yy4 = Convert.ToInt16(sidey4[indeks2]);

                        xx3 = xx1;
                        yy3 = yy4;

                       
                    }
                    else
                    {


                        indeks1 = 0; indeks2 = 0;
                        temp = 1000.00;
                        i = 0; j = 0;

                        while (i < sisix3.Count)
                        {
                            j = 0;
                            while (j < sidex3.Count)
                            {
                                if ((int)sisix3[i] == (int)sidex3[j])
                                {

                                    indeks1 = i;
                                    indeks2 = j;
                                    if (Convert.ToInt16(sidex1[indeks2]) < Convert.ToInt16(sisix4[indeks1]) && Convert.ToInt16(sidey1[indeks2]) < Convert.ToInt16(sisiy4[indeks1]))
                                    {
                                        temp = 0;
                                        break;
                                    }
                                }
                                j++;
                            }
                            if (temp == 0)
                                break;
                            i++;
                        }
                        if (temp == 0)
                        {
                           
                            xx1 = Convert.ToInt16(sidex1[indeks2]);
                            yy1 = Convert.ToInt16(sidey1[indeks2]);

                            xx3 = Convert.ToInt16(sisix3[indeks1]);
                            yy3 = Convert.ToInt16(sisiy3[indeks1]);

                            xx4 = Convert.ToInt16(sisix4[indeks1]);
                            yy4 = Convert.ToInt16(sisiy4[indeks1]);

                            xx2 = xx4;
                            yy2 = yy1;
                        }
                        else
                        {

                            indeks1 = 0; indeks2 = 0;
                            temp = 1000.00;
                            i = 0; j = 0;

                            while (i < sisix4.Count)
                            {
                                //Console.WriteLine("i: " + i);
                                j = 0;
                                while (j < sidex4.Count)
                                {
                                    //Console.WriteLine("j: " + j);
                                    if ((int)sisix4[i] == (int)sidex4[j])
                                    {
                                        indeks1 = i;
                                        indeks2 = j;
                                        if (Convert.ToInt16(sisix3[indeks1]) < Convert.ToInt16(sidex2[indeks2]) && Convert.ToInt16(sisiy3[indeks1]) > Convert.ToInt16(sidey2[indeks2]))
                                        {

                                            temp = 0;
                                            break;
                                        }
                                    }
                                    j++;
                                }
                                if (temp == 0)
                                    break;
                                i++;
                            }
                            if (temp == 0)
                            {

                                xx2 = Convert.ToInt16(sidex2[indeks2]);
                                yy2 = Convert.ToInt16(sidey2[indeks2]);

                                xx3 = Convert.ToInt16(sisix3[indeks1]);
                                yy3 = Convert.ToInt16(sisiy3[indeks1]);

                                xx4 = Convert.ToInt16(sisix4[indeks1]);
                                yy4 = Convert.ToInt16(sisiy4[indeks1]);

                                xx1 = xx3;
                                yy1 = yy2;

                            }
                            else
                            {
                                xx1 = 0;
                                yy1 = 0;
                                xx2 = 0;
                                yy2 = 0;
                                xx3 = 0;
                                yy3 = 0;
                                xx4 = 0;
                                yy4 = 0;
                            }

                        }
                    }


                }
                
                //Console.WriteLine("Marker tidak terdeteksi");
                xx1 = 0;
                yy1 = 0;
                xx2 = 0;
                yy2 = 0;
                xx3 = 0;
                yy3 = 0;
                xx4 = 0;
                yy4 = 0;

            }
            
            hasil[0, 0] = xx1;
            hasil[0, 1] = yy1;
            hasil[1, 0] = xx2;
            hasil[1, 1] = yy2;

            hasil[2, 0] = xx3;
            hasil[2, 1] = yy3;

            hasil[3, 0] = xx4;
            hasil[3, 1] = yy4;
            return hasil;

        }

        


        public void drawEllipse(PictureBox pb, ArrayList x1, ArrayList y1, ArrayList x2, ArrayList y2, ArrayList x3, ArrayList y3, ArrayList x4, ArrayList y4,
            int w, int h, float Bwidth, Color col)
        {
            //refresh the picture box
            // pb.Refresh();
            //create a graphics object
            Graphics g = pb.CreateGraphics();
            //create a pen object
            Pen p = new Pen(col, Bwidth);
            Pen p2 = new Pen(Color.Blue, Bwidth);
            Pen p3 = new Pen(Color.LimeGreen, Bwidth);
            Pen p4 = new Pen(Color.Orange, Bwidth);
            //draw Ellipse
            for (int i = 0; i < x1.Count; i++)
            {
                int x = Convert.ToInt32(x1[i]);
                int y = Convert.ToInt32(y1[i]);
                g.DrawEllipse(p, x, y, w, h);
            }

            for (int i = 0; i < x2.Count; i++)
            {
                int x = Convert.ToInt32(x2[i]);
                int y = Convert.ToInt32(y2[i]);
                g.DrawEllipse(p2, x, y, w, h);
            }

            for (int i = 0; i < x3.Count; i++)
            {
                int x = Convert.ToInt32(x3[i]);
                int y = Convert.ToInt32(y3[i]);
                g.DrawEllipse(p3, x, y, w, h);
            }

            for (int i = 0; i < x4.Count; i++)
            {
                int x = Convert.ToInt32(x4[i]);
                int y = Convert.ToInt32(y4[i]);
                g.DrawEllipse(p4, x, y, w, h);
            }

            //dispose pen and graphics object
            p.Dispose();
            g.Dispose();
        }

        public void drawEllipse(PictureBox pb, int x1, int y1,
            int w, int h, float Bwidth, Color col)
        {
            //refresh the picture box
            // pb.Refresh();
            //create a graphics object
            Graphics g = pb.CreateGraphics();
            //create a pen object
            Pen p = new Pen(col, Bwidth);
            Pen p2 = new Pen(Color.Blue, Bwidth);
            Pen p3 = new Pen(Color.LimeGreen, Bwidth);
            Pen p4 = new Pen(Color.Orange, Bwidth);
            //draw Ellipse
           // for (int i = 0; i < x1.Count; i++)
            //{
                int x = x1;
                int y = y1;
                g.DrawEllipse(p, x, y, w, h);
            //}

            //dispose pen and graphics object
            p.Dispose();
            g.Dispose();
        }

        private void drawline(PictureBox pb, Point p1, Point p2, float Bwidth, Color c1)
        {
            //refresh the picture box
            //pb.Refresh();
            //create a new Bitmap object
            Bitmap map = (Bitmap)pb.Image;
            //create a graphics object
            Graphics g = Graphics.FromImage(map);
            //create a pen object and setting the color and width for the pen
            Pen p = new Pen(c1, Bwidth);
            //draw line between  point p1 and p2
            g.DrawLine(p, p1, p2);
         
            pb.Image = map;
            //dispose pen and graphics object
            p.Dispose();
            g.Dispose();
        }

       
        private void warnaSegiEmpat(PictureBox pb, int x1, int y1, int x2, int y2, int x3, int y3, int x4, int y4, Color c)
        {
            drawline(pb, new Point(x1, y1), new Point(x2, y2), 3, c);
            drawline(pb, new Point(x3, y3), new Point(x4, y4), 3, c);
            drawline(pb, new Point(x1, y1), new Point(x3, y3), 3, c);
            drawline(pb, new Point(x2, y2), new Point(x4, y4), 3, c);
            
        }

        public double PotongX = 0, PotongY = 0;
        double jarakP = 0, jarakL = 0;
        public double rasio;
      
        public int idealx1 = 0, idealy1 = 0, idealx2 = 0, idealy2 = 0, idealx3 = 0, idealy3 = 0, idealx4 = 0, idealy4 = 0;
      
        int translasiX = 0, translasiY = 0;

        public double beta = 0, gamma = 0, alfa = 0;

        public int[] result;
        public int[] daerah;
        public double nilaiFokus = 0;

        public int[] titikPotong(int[,] EdgeMap, int xx1, int yy1, int xx2, int yy2, int xx3, int yy3, int xx4, int yy4)
        {
            int tempx1 = 0, tempy1 = 0, tempx2 = 0, tempy2 = 0, tempx3 = 0, tempy3 = 0, tempx4 = 0, tempy4 = 0;
            result = new int[10];
            daerah = new int[5];
                 int[]koordinatX = new int[5];
                 int[] koordinatY = new int[5];

                koordinatX[0] = xx1;
                koordinatX[1] = xx2;
                koordinatX[2] = xx3;
                koordinatX[3] = xx4;

                koordinatY[0] = yy1;
                koordinatY[1] = yy2;
                koordinatY[2] = yy3;
                koordinatY[3] = yy4;

                int i = 0;

                while (i < koordinatX.Length)
                {

                    if (koordinatX[i] < 180)
                    {

                        koordinatX[i] = (180 - koordinatX[i]) * -1;


                    }
                    else
                    {

                        koordinatX[i] = (koordinatX[i] - 180);

                    }

                    if (koordinatY[i] < 120)
                    {
                        koordinatY[i] = (120 - koordinatY[i]);
                    }
                    else
                    {
                        koordinatY[i] = (koordinatY[i] - 120) * -1;
                    }

                    i++;

                }


                int y1 = 1, y2 = 1;
                
                double dx1 = koordinatX[3] - koordinatX[0];
                double dy1 = koordinatY[3] - koordinatY[0];

                double m1 = dy1 / dx1;
                //Console.WriteLine("M1: " + m1);
                double c1 = koordinatY[0] - m1 * koordinatX[0];
                //Console.WriteLine("c1: " + c1);

                double dx2 = koordinatX[2] - koordinatX[1];
                double dy2 = koordinatY[2] - koordinatY[1];
                double m2 = dy2 / dx2;
                //Console.WriteLine("M2: " + m2);
                double c2 = koordinatY[1] - m2 * koordinatX[1];
                //Console.WriteLine("c2: " + c2);

                m2 *= -1;
                m1 *= -1;

                if ((y1 * m2 - y2 * m1 != 0) && (m1 * y2 - m2 * y1 != 0))
                {
                    PotongX = (c1 * y2 - c2 * y1) / (m1 * y2 - y1 * m2);
                    PotongY = (c2 * m1 - c1 * m2) / (m1 * y2 - y1 * m2);


                    translasiX = (int)PotongX;
                    translasiY = (int)PotongY;

                    PotongX += 180;
                    if (PotongY < 0)
                    {
                        PotongY = 120 + PotongY * -1;
                    }
                    else
                    {
                        PotongY = 120 - PotongY;
                    }

                }


                jarakP = Math.Sqrt((yy2 - yy1) * (yy2 - yy1) + (xx2 - xx1) * (xx2 - xx1));
                jarakL = Math.Sqrt((yy3 - yy1) * (yy3 - yy1) + (xx3 - xx1) * (xx3 - xx1));


                rasio = jarakP / 360;
                double rasio2 = jarakL / 240;
                panjang = (int)(360 * rasio);
                lebar = (int)(240 * rasio);
                tinggi = (int)(240 * rasio);

                if (Double.IsNaN(PotongX) == false && Double.IsNaN(PotongY) == false && PotongX > 0 && PotongY > 0 && PotongX < 360 && PotongY < 240)
                {
                    try
                    {
                        int arah = 0;

                        koordinatX[0] = (int)koordinatX[0] - translasiX;
                        koordinatX[1] = (int)koordinatX[1] - translasiX;
                        koordinatX[2] = (int)koordinatX[2] - translasiX;
                        koordinatX[3] = (int)koordinatX[3] - translasiX;

                        koordinatY[0] = (int)koordinatY[0] - translasiY;
                        koordinatY[1] = (int)koordinatY[1] - translasiY;
                        koordinatY[2] = (int)koordinatY[2] - translasiY;
                        koordinatY[3] = (int)koordinatY[3] - translasiY;




                        double jarakP1 = Math.Sqrt(((Convert.ToDouble(koordinatY[0]) - Convert.ToDouble(koordinatY[1])) * (Convert.ToDouble(koordinatY[0])
                            - Convert.ToDouble(koordinatY[1]))
                            + (Convert.ToDouble(koordinatX[0]) - Convert.ToDouble(koordinatX[1])) * (Convert.ToDouble(koordinatX[0]) - Convert.ToDouble(koordinatX[1]))));

                        double jarakP2 = Math.Sqrt(((Convert.ToDouble(koordinatY[2]) - Convert.ToDouble(koordinatY[3])) * (Convert.ToDouble(koordinatY[2])
                            - Convert.ToDouble(koordinatY[3]))
                            + (Convert.ToDouble(koordinatX[2]) - Convert.ToDouble(koordinatX[3])) * (Convert.ToDouble(koordinatX[2]) - Convert.ToDouble(koordinatX[3]))));

                        double jarakL1 = Math.Sqrt(((Convert.ToDouble(koordinatY[0]) - Convert.ToDouble(koordinatY[2])) * (Convert.ToDouble(koordinatY[0])
                            - Convert.ToDouble(koordinatY[2]))
                            + (Convert.ToDouble(koordinatX[0]) - Convert.ToDouble(koordinatX[2])) * (Convert.ToDouble(koordinatX[0]) - Convert.ToDouble(koordinatX[2]))));

                        double jarakL2 = Math.Sqrt(((Convert.ToDouble(koordinatY[1]) - Convert.ToDouble(koordinatY[3])) * (Convert.ToDouble(koordinatY[1])
                             - Convert.ToDouble(koordinatY[3]))
                             + (Convert.ToDouble(koordinatX[1]) - Convert.ToDouble(koordinatX[3])) * (Convert.ToDouble(koordinatX[1]) - Convert.ToDouble(koordinatX[3]))));


                        jarakP1 = (jarakP1 + jarakP2) / 2;
                        jarakL1 = (jarakL1 + jarakL2) / 2;


                        idealx1 = (int)(jarakP1 / 2 * -1);
                        idealy1 = (int)(jarakL1 / 2);

                        idealx2 = (int)(jarakP1 / 2);
                        idealy2 = (int)(jarakL1 / 2);

                        idealx3 = idealx1;
                        idealy3 = idealy1 * -1;

                        idealx4 = idealx2;
                        idealy4 = idealy2 * -1;

                        int tengahX12 = (xx1 + xx2) / 2;
                        int tengahY12 = (yy1 + yy2) / 2;

                        int tengahX34 = (xx3 + xx4) / 2;
                        int tengahY34 = (yy3 + yy4) / 2;

                        int tengahX13 = (xx1 + xx3) / 2;
                        int tengahY13 = (yy1 + yy3) / 2;

                        int tengahX24 = (xx2 + xx4) / 2;
                        int tengahY24 = (yy2 + yy4) / 2;


                        daerah[0] = EdgeMap[((int)PotongX + tengahX24) / 2, ((int)PotongY + tengahY24) / 2]; //kanan
                        daerah[1] = EdgeMap[((int)PotongX + tengahX13) / 2, ((int)PotongY + tengahY13) / 2]; //kiri
                        daerah[2] = EdgeMap[((int)PotongX + tengahX12) / 2, ((int)PotongY + tengahY12) / 2]; //atas
                        daerah[3] = EdgeMap[((int)PotongX + tengahX34) / 2, ((int)PotongY + tengahY34) / 2]; //bawah               

                        tempx1 = (int)koordinatX[0];
                        tempy1 = (int)koordinatY[0];

                        tempx2 = (int)koordinatX[1];
                        tempy2 = (int)koordinatY[1];

                        tempx3 = (int)koordinatX[2];
                        tempy3 = (int)koordinatY[2];

                        tempx4 = (int)koordinatX[3];
                        tempy4 = (int)koordinatY[3];

                        int max = 0, min = 1000;
                        for (int k = 0; k < 4; k++)
                        {
                            if (daerah[k] < min)
                                min = daerah[k];
                            if (daerah[k] > max)
                                max = daerah[k];
                        }

                        int batas = (min + max) / 2;
                        if (daerah[2] > batas && daerah[3] < batas)
                        {
                            arah = 1;
                            //kanan atas
                            if (daerah[1] < batas)
                            {
                                if ((int)koordinatY[1] > idealy2)
                                {
                                    //puter ke kanan
                                    koordinatX[0] = tempx2;
                                    koordinatY[0] = tempy2;

                                    koordinatX[1] = tempx4;
                                    koordinatY[1] = tempy4;

                                    koordinatX[2] = tempx1;
                                    koordinatY[2] = tempy1;

                                    koordinatX[3] = tempx3;
                                    koordinatY[3] = tempy3;
                                }
                            }
                            else if (daerah[0] < batas)//kiri atas
                            {
                                if ((int)koordinatY[1] < idealy2)
                                {
                                    //puter ke kiri
                                    koordinatX[0] = tempx3;
                                    koordinatY[0] = tempy3;

                                    koordinatX[1] = tempx1;
                                    koordinatY[1] = tempy1;

                                    koordinatX[2] = tempx4;
                                    koordinatY[2] = tempy4;

                                    koordinatX[3] = tempx2;
                                    koordinatY[3] = tempy2;
                                }
                            }
                        }
                        else if (daerah[2] < batas && daerah[3] > batas)
                        {
                            arah = 2;
                            if (daerah[0] < batas)//kiri bawah
                            {
                                if ((int)koordinatY[3] > idealy4)
                                {
                                    koordinatX[0] = tempx3;
                                    koordinatY[0] = tempy3;

                                    koordinatX[1] = tempx1;
                                    koordinatY[1] = tempy1;

                                    koordinatX[2] = tempx4;
                                    koordinatY[2] = tempy4;

                                    koordinatX[3] = tempx2;
                                    koordinatY[3] = tempy2;
                                }
                                else
                                {
                                    koordinatX[0] = tempx4;
                                    koordinatY[0] = tempy4;

                                    koordinatX[1] = tempx3;
                                    koordinatY[1] = tempy3;

                                    koordinatX[2] = tempx2;
                                    koordinatY[2] = tempy2;

                                    koordinatX[3] = tempx1;
                                    koordinatY[3] = tempy1;
                                }
                            }
                            else if (daerah[1] < batas)
                            {
                                if ((int)koordinatY[3] > idealy4)
                                {

                                    koordinatX[0] = tempx4;
                                    koordinatY[0] = tempy4;

                                    koordinatX[1] = tempx3;
                                    koordinatY[1] = tempy3;

                                    koordinatX[2] = tempx2;
                                    koordinatY[2] = tempy2;

                                    koordinatX[3] = tempx1;
                                    koordinatY[3] = tempy1;
                                }
                                else
                                {

                                    koordinatX[0] = tempx2;
                                    koordinatY[0] = tempy2;

                                    koordinatX[1] = tempx4;
                                    koordinatY[1] = tempy4;

                                    koordinatX[2] = tempx1;
                                    koordinatY[2] = tempy1;

                                    koordinatX[3] = tempx3;
                                    koordinatY[3] = tempy3;
                                }
                            }
                            else
                            {

                                koordinatX[0] = tempx4;
                                koordinatY[0] = tempy4;

                                koordinatX[1] = tempx3;
                                koordinatY[1] = tempy3;

                                koordinatX[2] = tempx2;
                                koordinatY[2] = tempy2;

                                koordinatX[3] = tempx1;
                                koordinatY[3] = tempy1;
                            }
                        }
                        else if (daerah[2] > batas && daerah[3] > batas)
                        {
                            //arah = 2;
                            if (daerah[0] < batas)
                            {

                                koordinatX[0] = tempx3;
                                koordinatY[0] = tempy3;

                                koordinatX[1] = tempx1;
                                koordinatY[1] = tempy1;

                                koordinatX[2] = tempx4;
                                koordinatY[2] = tempy4;

                                koordinatX[3] = tempx2;
                                koordinatY[3] = tempy2;
                            }
                            else if (daerah[1] < batas)
                            {

                                koordinatX[0] = tempx2;
                                koordinatY[0] = tempy2;

                                koordinatX[1] = tempx4;
                                koordinatY[1] = tempy4;

                                koordinatX[2] = tempx1;
                                koordinatY[2] = tempy1;

                                koordinatX[3] = tempx3;
                                koordinatY[3] = tempy3;
                            }
                        }

                        double miringIdeal = Math.Sqrt(idealx2 * idealx2 + idealy2 * idealy2);
                        double miringMarker = Math.Sqrt(Convert.ToDouble(koordinatX[1]) * Convert.ToDouble(koordinatX[1]) + Convert.ToDouble(koordinatY[1]) * Convert.ToDouble(koordinatY[1]));

                        double sudutIdeal = Math.Acos((idealx2 / miringIdeal)) * 180 / Math.PI;

                        if ((int)koordinatY[1] < 0 && (int)koordinatX[1] < 0)
                        {
                            //kuadran 3
                            sudutIdeal -= 180;
                        }
                        else if ((int)koordinatY[1] < 0 && (int)koordinatX[1] > 0)
                        {
                            //kuadran 4
                            sudutIdeal -= 90;
                        }
                        else if ((int)koordinatY[1] > 0 && (int)koordinatX[1] < 0)
                        {
                            //kuadran 2
                            sudutIdeal += 90;
                        }

                        double sudutMarker = Math.Acos((Math.Abs(Convert.ToDouble(koordinatX[1])) / miringMarker)) * 180 / Math.PI;

                        gamma = Math.Abs(sudutIdeal - sudutMarker);


                        if (arah == 1)
                        {
                            if ((int)koordinatX[3] < (int)koordinatX[1])
                            {
                                gamma = -1 * gamma;
                            }
                        }
                        else
                        {
                            if ((int)koordinatX[3] < (int)koordinatX[1])
                            {
                                gamma = -1 * gamma;
                            }
                        }


                        int kornerX13 = (int)koordinatX[0] + (int)koordinatX[2];
                        int kornerX24 = (int)koordinatX[1] + (int)koordinatX[3];

                        int panjangIdeal = 240;
                        int lebarIdeal = 240;

                        double z1 = ((jarakP1 / panjangIdeal * nilaiFokus) + (jarakL1 / lebarIdeal * nilaiFokus)) / 2;
                        double z2 = ((jarakP1 / panjangIdeal * nilaiFokus) + (jarakL2 / lebarIdeal * nilaiFokus)) / 2;
                        double z3 = ((jarakP2 / panjangIdeal * nilaiFokus) + (jarakL1 / lebarIdeal * nilaiFokus)) / 2;
                        double z4 = ((jarakP2 / panjangIdeal * nilaiFokus) + (jarakL2 / lebarIdeal * nilaiFokus)) / 2;

                        beta = (double)(kornerX13 + kornerX24) / (z1 + z2 + z3 + z4);
                        beta = Math.Asin(beta) * 180 / Math.PI;

                        int kornerY13 = (int)koordinatY[0] + (int)koordinatY[1];
                        int kornerY24 = (int)koordinatY[2] + (int)koordinatY[3];

                        double z = (z1 + z2 + z3 + z4) * -1;
                        alfa = (double)(kornerY13 + kornerY24) / z;
                        alfa /= Math.Cos(beta * Math.PI / 180);
                        alfa = Math.Asin(alfa) * 180 / Math.PI;
                    }
                    catch (OverflowException)
                    {                       
                    } 
                }
               
                result[0] = (int)PotongX;
                result[1] = (int)PotongY;
                result[2] = panjang;
                result[3] = lebar;
                result[4] = tinggi;
                result[5] = (int)alfa;
                result[6] = (int)beta;
                result[7] = (int)gamma;
                return result;

        }
    }
}
