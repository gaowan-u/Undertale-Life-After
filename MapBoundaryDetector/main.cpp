#include <opencv2/opencv.hpp>
#include <vector>
#include <string>
#include <fstream>
#include <nlohmann/json.hpp>

using namespace cv;
using namespace std;
using json = nlohmann::json;

class MapBoundaryDetector {
private:
    // 简化轮廓点（使用Douglas-Peucker算法）
    vector<Point> simplifyContour(const vector<Point>& contour, double epsilon = 3.0) {
        vector<Point> simplified;
        approxPolyDP(contour, simplified, epsilon, true);
        return simplified;
    }
    
    // 处理边界，保持右侧开口不闭合，但保留所有边界点
    vector<Point> removeExitBoundary(const vector<Point>& contour, int imageWidth) {
        if (contour.empty()) return contour;
        
        // 找到最右侧的点作为开口位置
        int maxX = 0;
        int maxIdx = 0;
        for (size_t i = 0; i < contour.size(); i++) {
            if (contour[i].x > maxX) {
                maxX = contour[i].x;
                maxIdx = i;
            }
        }
        
        // 从最右侧点的下一个点开始，重新排列轮廓点
        // 这样首尾点都在最右侧附近，形成开口
        vector<Point> result;
        for (size_t i = 0; i < contour.size(); i++) {
            size_t idx = (maxIdx + 1 + i) % contour.size();
            result.push_back(contour[idx]);
        }
        
        return result;
    }

public:
    // 检测地图边界
    vector<Point> detectBoundary(const Mat& image) {
        Mat hsv, mask;
        
        // 转换为HSV颜色空间
        cvtColor(image, hsv, COLOR_BGR2HSV);
        
        // 定义深蓝色的范围（地图背景色）
        // 地图是深蓝色/紫色
        Scalar lowerBlue(100, 40, 40);
        Scalar upperBlue(130, 255, 255);
        
        // 创建掩码
        inRange(hsv, lowerBlue, upperBlue, mask);
        
        // 形态学操作，去除噪点
        Mat kernel = getStructuringElement(MORPH_RECT, Size(3, 3));
        morphologyEx(mask, mask, MORPH_CLOSE, kernel);
        morphologyEx(mask, mask, MORPH_OPEN, kernel);
        
        // 查找轮廓
        vector<vector<Point>> contours;
        vector<Vec4i> hierarchy;
        findContours(mask, contours, hierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
        
        if (contours.empty()) {
            cout << "未检测到轮廓！" << endl;
            return vector<Point>();
        }
        
        // 找到最大的轮廓（地图边界）
        int maxIdx = 0;
        double maxArea = 0;
        for (size_t i = 0; i < contours.size(); i++) {
            double area = contourArea(contours[i]);
            if (area > maxArea) {
                maxArea = area;
                maxIdx = i;
            }
        }
        
        cout << "检测到最大轮廓面积: " << maxArea << endl;
        
        // 简化轮廓
        vector<Point> simplified = simplifyContour(contours[maxIdx], 3.0);
        
        // 移除右侧出口部分
        vector<Point> finalBoundary = removeExitBoundary(simplified, image.cols);
        
        return finalBoundary;
    }
    
    // 保存边界坐标到JSON文件
    bool saveBoundaryToJSON(const vector<Point>& boundary, const string& filename, 
                           int imageWidth, int imageHeight) {
        json jsonData;
        
        jsonData["image_width"] = imageWidth;
        jsonData["image_height"] = imageHeight;
        jsonData["boundary_points_count"] = boundary.size();
        
        json pointsArray = json::array();
        for (const auto& pt : boundary) {
            pointsArray.push_back({
                {"x", pt.x},
                {"y", pt.y}
            });
        }
        
        jsonData["boundary_points"] = pointsArray;
        
        // 计算边界框（用于快速碰撞检测）
        if (!boundary.empty()) {
            int minX = boundary[0].x, maxX = boundary[0].x;
            int minY = boundary[0].y, maxY = boundary[0].y;
            
            for (const auto& pt : boundary) {
                minX = min(minX, pt.x);
                maxX = max(maxX, pt.x);
                minY = min(minY, pt.y);
                maxY = max(maxY, pt.y);
            }
            
            jsonData["bounding_box"] = {
                {"min_x", minX},
                {"max_x", maxX},
                {"min_y", minY},
                {"max_y", maxY}
            };
        }
        
        ofstream outFile(filename);
        if (!outFile.is_open()) {
            cout << "无法打开文件: " << filename << endl;
            return false;
        }
        
        outFile << jsonData.dump(4) << endl;
        outFile.close();
        
        cout << "边界坐标已保存到: " << filename << endl;
        cout << "边界点数量: " << boundary.size() << endl;
        
        return true;
    }
    
    // 绘制边界
    void drawBoundary(Mat& image, const vector<Point>& boundary, Scalar color = Scalar(0, 255, 0), 
                     int thickness = 2) {
        if (boundary.empty()) return;
        
        // 绘制轮廓线
        for (size_t i = 0; i < boundary.size() - 1; i++) {
            line(image, boundary[i], boundary[i + 1], color, thickness);
        }
        
        // 绘制点
        for (const auto& pt : boundary) {
            circle(image, pt, 3, Scalar(0, 255, 0), -1);
        }
    }
    
    // 检查点是否在地图边界内
    bool isPointInsideBoundary(const Point& point, const vector<Point>& boundary) {
        if (boundary.empty()) return false;
        
        // 使用射线法判断点是否在多边形内
        bool inside = false;
        int j = boundary.size() - 1;
        
        for (size_t i = 0; i < boundary.size(); i++) {
            if (((boundary[i].y > point.y) != (boundary[j].y > point.y)) &&
                (point.x < (boundary[j].x - boundary[i].x) * (point.y - boundary[i].y) / 
                            (boundary[j].y - boundary[i].y) + boundary[i].x)) {
                inside = !inside;
            }
            j = i;
        }
        
        return inside;
    }
};

int main() {
    // 读取图像
    Mat image = imread("map_input.png");
    if (image.empty()) {
        cout << "错误：无法读取图像文件！" << endl;
        return -1;
    }
    
    cout << "图像尺寸: " << image.cols << " x " << image.rows << endl;
    
    // 创建边界检测器
    MapBoundaryDetector detector;
    
    // 检测边界
    cout << "\n正在检测地图边界..." << endl;
    vector<Point> boundary = detector.detectBoundary(image);
    
    if (boundary.empty()) {
        cout << "错误：未检测到地图边界！" << endl;
        return -1;
    }
    
    // 保存边界到JSON文件
    string jsonFile = "map_boundary.json";
    detector.saveBoundaryToJSON(boundary, jsonFile, image.cols, image.rows);
    
    // 在图像上绘制边界
    Mat result = image.clone();
    detector.drawBoundary(result, boundary, Scalar(0, 255, 0), 2);
    
    // 测试碰撞检测
    Point testPoint1(image.cols / 2, image.rows / 2);  // 中心点（应该在内部）
    Point testPoint2(10, 10);  // 左上角（应该在外部）
    
    cout << "\n碰撞检测测试:" << endl;
    cout << "中心点 (" << testPoint1.x << ", " << testPoint1.y << ") 在地图内: " 
         << (detector.isPointInsideBoundary(testPoint1, boundary) ? "是" : "否") << endl;
    cout << "左上角点 (" << testPoint2.x << ", " << testPoint2.y << ") 在地图内: " 
         << (detector.isPointInsideBoundary(testPoint2, boundary) ? "是" : "否") << endl;
    
    // 保存结果图像
    imwrite("map_boundary_result.png", result);
    cout << "\n结果图像已保存到: map_boundary_result.png" << endl;
    
    return 0;
}
